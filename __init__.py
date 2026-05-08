import os
import sys
import json
import subprocess
import threading
import folder_paths
from server import PromptServer
from aiohttp import web

# Developer: Marbycore
# GitHub: https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically

# ─── MANAGER MODEL DB CACHE ──────────────────────────────────────────────────
MANAGER_DB_URL = "https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/model-list.json"
_manager_db_cache = None

def get_manager_model_db():
    """
    Returns a dict of {filename: model_info} from ComfyUI-Manager's database.
    Priority: local cache file → online fetch.
    """
    global _manager_db_cache
    if _manager_db_cache is not None:
        return _manager_db_cache

    db = {}

    # 1. Try local ComfyUI-Manager cache first (fastest, works offline)
    try:
        manager_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ComfyUI-Manager")
        db_path = os.path.join(manager_path, "node_db", "model-list.json")
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                for m in data.get('models', []):
                    if m.get('filename') and m.get('url'):
                        db[m['filename']] = m
            print(f"[AutoModelDownloader] Loaded {len(db)} models from local Manager DB")
    except Exception as e:
        print(f"[AutoModelDownloader] Local Manager DB error: {e}")

    # 2. Try fetching online if local was empty (runs in background, updates cache)
    if not db:
        try:
            import urllib.request
            with urllib.request.urlopen(MANAGER_DB_URL, timeout=10) as r:
                data = json.loads(r.read().decode())
                for m in data.get('models', []):
                    if m.get('filename') and m.get('url'):
                        db[m['filename']] = m
            print(f"[AutoModelDownloader] Loaded {len(db)} models from online Manager DB")
        except Exception as e:
            print(f"[AutoModelDownloader] Online Manager DB error: {e}")

    _manager_db_cache = db
    return db

# ─── LOCAL PRIORITY REGISTRY ─────────────────────────────────────────────────
try:
    from .model_registry import BUILTIN_REGISTRY
except ImportError:
    BUILTIN_REGISTRY = {}

# ─── NODE TYPE → COMFYUI FOLDER MAPPING ─────────────────────────────────────
NODE_TO_FOLDER = {
    "UNETLoader":               "diffusion_models",
    "CheckpointLoader":         "checkpoints",
    "CheckpointLoaderSimple":   "checkpoints",
    "VAELoader":                "vae",
    "CLIPLoader":               "text_encoders",
    "DualCLIPLoader":           "text_encoders",
    "TripleCLIPLoader":         "text_encoders",
    "LoraLoader":               "loras",
    "LoraLoaderModelOnly":      "loras",
    "ControlNetLoader":         "controlnet",
    "UpscaleModelLoader":       "upscale_models",
    "CLIPVisionLoader":         "clip_vision",
    "IPAdapterModelLoader":     "ipadapter",
    "PhotoMakerLoader":         "photomaker",
}

def find_model_path(filename):
    """Search all ComfyUI model folders for a given filename."""
    for folder_name in folder_paths.folder_names_and_paths:
        try:
            for base in folder_paths.folder_names_and_paths[folder_name][0]:
                if os.path.exists(os.path.join(base, filename)):
                    return os.path.join(base, filename)
        except Exception:
            continue
    return None

def get_missing_models(prompt):
    """
    Analyze a ComfyUI prompt (API format) and return a list of missing models.
    Automatically discovers download URLs from ComfyUI-Manager's database.
    """
    missing = []
    seen = set()
    manager_db = get_manager_model_db()

    for node_id, node_data in prompt.items():
        if not isinstance(node_data, dict):
            continue

        ntype = node_data.get("class_type", "")
        inputs = node_data.get("inputs", {})
        target_folder = NODE_TO_FOLDER.get(ntype)

        for key, val in inputs.items():
            if not isinstance(val, str):
                continue
            if not any(val.endswith(ext) for ext in
                       ['.safetensors', '.gguf', '.pt', '.bin', '.ckpt', '.pth']):
                continue
            if val in seen:
                continue
            seen.add(val)

            if find_model_path(val):
                continue  # Already installed

            print(f"[AutoModelDownloader] MISSING: {val}")

            # Build model entry — URL from registry, Manager DB, or unknown
            entry = {
                "filename": val,
                "folder":   target_folder or "other",
                "url":      None
            }

            if val in BUILTIN_REGISTRY:
                entry["folder"] = BUILTIN_REGISTRY[val].get("folder", entry["folder"])
                entry["url"]    = BUILTIN_REGISTRY[val]["url"]
            elif val in manager_db:
                info = manager_db[val]
                entry["folder"] = info.get("save_path", entry["folder"])
                entry["url"]    = info.get("url")

            missing.append(entry)

    return missing

# ─── CONSOLE LAUNCHER ────────────────────────────────────────────────────────
def launch_downloader(missing_models):
    """Open a dedicated console window with the visual downloader."""
    script = os.path.join(os.path.dirname(__file__), "downloader_console.py")
    tmp    = os.path.join(os.path.dirname(__file__), "_pending_downloads.json")

    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(missing_models, f, ensure_ascii=False)

    cmd = [sys.executable, script, tmp]
    try:
        if sys.platform == "win32":
            subprocess.Popen(
                ['cmd', '/c', 'start', 'cmd', '/k'] + cmd,
                creationflags=subprocess.CREATE_NEW_CONSOLE
            )
        elif sys.platform == "darwin":
            subprocess.Popen(
                ['osascript', '-e',
                 f'tell application "Terminal" to do script "{" ".join(cmd)}"']
            )
        else:
            launched = False
            for term in ["gnome-terminal", "konsole", "xfce4-terminal", "xterm"]:
                try:
                    subprocess.Popen([term, '--', *cmd])
                    launched = True
                    break
                except FileNotFoundError:
                    continue
            if not launched:
                # Fallback: run in current console (no new window)
                subprocess.Popen(cmd)
    except Exception as e:
        print(f"[AutoModelDownloader] Error launching console: {e}")

# ─── API ENDPOINT ─────────────────────────────────────────────────────────────
@PromptServer.instance.routes.post('/auto_downloader/check')
async def check_models(request):
    try:
        data    = await request.json()
        prompt  = data.get('prompt', {})
        missing = get_missing_models(prompt)

        if missing:
            launch_downloader(missing)
            return web.json_response({
                "status": "missing",
                "count":  len(missing),
                "models": [m['filename'] for m in missing]
            })

        return web.json_response({"status": "ok", "count": 0})
    except Exception as e:
        print(f"[AutoModelDownloader] API error: {e}")
        return web.json_response({"status": "error", "message": str(e)}, status=500)

# ─── COMFYUI NODE REGISTRATION ───────────────────────────────────────────────
NODE_CLASS_MAPPINGS        = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY              = "./js"

print("\033[94m[AutoModelDownloader]\033[0m v2.1 ready — Developer: Marbycore")
