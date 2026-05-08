import os
import sys
import json
import subprocess
import threading
import re
import folder_paths
from server import PromptServer
from aiohttp import web

# Developer: Marbycore
# GitHub: https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically

# ─── MANAGER MODEL DB ────────────────────────────────────────────────────────
_manager_db       = {}
_manager_db_ready = threading.Event()

def _load_manager_db():
    global _manager_db
    loaded = {}
    try:
        manager_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "ComfyUI-Manager")
        db_path = os.path.join(manager_path, "node_db", "model-list.json")
        if os.path.exists(db_path):
            with open(db_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            for m in data.get('models', []):
                if m.get('filename') and m.get('url'):
                    loaded[m['filename']] = {**m, '_source': 'MANAGER_LOCAL'}
    except: pass
    
    try:
        import urllib.request
        with urllib.request.urlopen("https://raw.githubusercontent.com/ltdrdata/ComfyUI-Manager/main/model-list.json", timeout=10) as r:
            data = json.loads(r.read().decode())
        for m in data.get('models', []):
            if m.get('filename') and m.get('url') and m['filename'] not in loaded:
                loaded[m['filename']] = {**m, '_source': 'MANAGER_ONLINE'}
    except: pass

    _manager_db = loaded
    _manager_db_ready.set()
    print(f"[AutoModelDownloader] Model DB Ready ({len(_manager_db)} models)")

threading.Thread(target=_load_manager_db, daemon=True).start()

# ─── LOCAL PRIORITY REGISTRY ─────────────────────────────────────────────────
try:
    from .model_registry import BUILTIN_REGISTRY
except:
    BUILTIN_REGISTRY = {}

def find_model_path(filename):
    for folder_name in folder_paths.folder_names_and_paths:
        try:
            for base in folder_paths.folder_names_and_paths[folder_name][0]:
                if os.path.exists(os.path.join(base, filename)):
                    return os.path.join(base, filename)
        except: continue
    return None

def get_missing_models(data):
    """
    Regex-based scanning: Fast, safe, and finds everything.
    """
    _manager_db_ready.wait(timeout=5)
    missing = []
    seen = set()

    # Convert everything to string and find filenames ending in extensions
    raw_text = json.dumps(data)
    # Find anything inside quotes that looks like a model filename
    pattern = r'"([^"]+\.(?:safetensors|gguf|pt|bin|ckpt|pth))"'
    matches = re.findall(pattern, raw_text, re.IGNORECASE)

    for val in matches:
        filename_only = os.path.basename(val.replace("\\", "/"))
        if filename_only in seen: continue
        seen.add(filename_only)

        if find_model_path(filename_only): continue

        folder = "checkpoints"
        if "vae" in filename_only.lower(): folder = "vae"
        elif "lora" in filename_only.lower(): folder = "loras"
        elif "control" in filename_only.lower(): folder = "controlnet"

        entry = {"filename": filename_only, "folder": folder, "url": None, "_source": "NOT_FOUND"}

        if filename_only in BUILTIN_REGISTRY:
            entry.update({
                "folder": BUILTIN_REGISTRY[filename_only].get("folder", folder),
                "url": BUILTIN_REGISTRY[filename_only]["url"],
                "_source": "BUILTIN"
            })
        elif filename_only in _manager_db:
            m = _manager_db[filename_only]
            entry.update({
                "folder": m.get("save_path", folder),
                "url": m.get("url"),
                "_source": m.get("_source", "MANAGER")
            })
        
        missing.append(entry)
    return missing

def launch_downloader(missing_models):
    script = os.path.join(os.path.dirname(__file__), "downloader_console.py")
    tmp = os.path.join(os.path.dirname(__file__), "_pending_downloads.json")
    with open(tmp, 'w', encoding='utf-8') as f:
        json.dump(missing_models, f, ensure_ascii=False)
    
    cmd = [sys.executable, script, tmp]
    if sys.platform == "win32":
        subprocess.Popen(['cmd', '/c', 'start', 'cmd', '/k'] + cmd, creationflags=subprocess.CREATE_NEW_CONSOLE)
    else:
        subprocess.Popen(cmd) # Fallback

@PromptServer.instance.routes.post('/auto_downloader/check')
async def check_models(request):
    try:
        data = await request.json()
        missing = get_missing_models(data)
        if missing:
            launch_downloader(missing)
            return web.json_response({"status": "missing", "count": len(missing)})
        return web.json_response({"status": "ok"})
    except:
        return web.json_response({"status": "ok"}) # Silent fail to never block ComfyUI

NODE_CLASS_MAPPINGS = {}
NODE_DISPLAY_NAME_MAPPINGS = {}
WEB_DIRECTORY = "./js"

print("\033[94m[AutoModelDownloader]\033[0m v2.9 Rescue Version - Active")
