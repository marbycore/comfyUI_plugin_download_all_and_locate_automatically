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

# ─── MANAGER MODEL DB ────────────────────────────────────────────────────────
MANAGER_DB_URL = "https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/model-list.json"

_manager_db       = {}   # populated at startup
_manager_db_ready = threading.Event()

def _load_manager_db():
    """
    Runs in a background thread at startup.
    Loads from local Manager cache first, then fetches online if needed.
    Signals _manager_db_ready when done so the first check waits properly.
    """
    global _manager_db

    loaded = {}

    # 1 — Local Manager cache (instant, works offline)
    try:
        manager_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ComfyUI-Manager")
        db_path = os.path.join(manager_path, "node_db", "model-list.json")
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for m in data.get('models', []):
                if m.get('filename') and m.get('url'):
                    loaded[m['filename']] = {**m, '_source': 'MANAGER_LOCAL'}
            print(f"[AutoModelDownloader] Local Manager DB: {len(loaded)} models")
    except Exception as e:
        print(f"[AutoModelDownloader] Local Manager DB error: {e}")

    # 2 — Online fetch (fills gaps the local cache may have)
    try:
        import urllib.request
        with urllib.request.urlopen(MANAGER_DB_URL, timeout=15) as r:
            data = json.loads(r.read().decode())
        online_added = 0
        for m in data.get('models', []):
            if m.get('filename') and m.get('url') and m['filename'] not in loaded:
                loaded[m['filename']] = {**m, '_source': 'MANAGER_ONLINE'}
                online_added += 1
        print(f"[AutoModelDownloader] Online Manager DB: +{online_added} extra models")
    except Exception as e:
        print(f"[AutoModelDownloader] Online Manager DB unavailable: {e}")

    _manager_db = loaded
    _manager_db_ready.set()
    print(f"[AutoModelDownloader] DB ready — {len(_manager_db)} models indexed")

# Start loading in background immediately at import time
threading.Thread(target=_load_manager_db, daemon=True, name="AutoDownloader-DBLoader").start()

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
    Analyze a ComfyUI prompt and return missing models with URLs and sources.
    Waits up to 20s for the Manager DB to be ready before checking.
    """
    # Wait for DB to finish loading (max 20s — avoids race condition)
    db_ready = _manager_db_ready.wait(timeout=20)
    if not db_ready:
        print("[AutoModelDownloader] Warning: DB not ready in time, checking with partial data")

    missing = []
    seen = set()

    for node_id, node_data in prompt.items():
        if not isinstance(node_data, dict):
            continue

        ntype  = node_data.get("class_type", "")
        inputs = node_data.get("inputs", {})
        target_folder = NODE_TO_FOLDER.get(ntype)

        for key, val in inputs.items():
            if not isinstance(val, str):
                continue
            if not any(val.lower().endswith(ext) for ext in
                       ['.safetensors', '.gguf', '.pt', '.bin', '.ckpt', '.pth']):
                continue
            
            # Smart Parsing: Extract filename from path (e.g. "t5\model.safetensors" -> "model.safetensors")
            filename_only = os.path.basename(val.replace("\\", "/"))
            
            if filename_only in seen:
                continue
            seen.add(filename_only)

            if find_model_path(filename_only):
                continue  # already installed

            print(f"[AutoModelDownloader] MISSING: {filename_only} (original string: {val})")

            entry = {"filename": filename_only, "folder": target_folder or "other", "url": None, "_source": "NOT_FOUND"}

            if filename_only in BUILTIN_REGISTRY:
                entry["folder"]  = BUILTIN_REGISTRY[filename_only].get("folder", entry["folder"])
                entry["url"]     = BUILTIN_REGISTRY[filename_only]["url"]
                entry["_source"] = "BUILTIN"
            elif filename_only in _manager_db:
                info = _manager_db[filename_only]
                entry["folder"]  = info.get("save_path", entry["folder"])
                entry["url"]     = info.get("url")
                entry["_source"] = info.get("_source", "MANAGER")

            missing.append(entry)


    return missing

# ─── CONSOLE LAUNCHER ─────────────────────────────────────────────────────────
def launch_downloader(missing_models):
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
            for term in ["gnome-terminal", "konsole", "xfce4-terminal", "xterm"]:
                try:
                    subprocess.Popen([term, '--', *cmd])
                    break
                except FileNotFoundError:
                    continue
    except Exception as e:
        print(f"[AutoModelDownloader] Error launching console: {e}")

# ─── API ENDPOINT ──────────────────────────────────────────────────────────────
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

# ─── COMFYUI REGISTRATION ─────────────────────────────────────────────────────
NODE_CLASS_MAPPINGS        = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY              = "./js"

print("\033[94m[AutoModelDownloader]\033[0m v2.2 — Developer: Marbycore (loading model DB...)")
