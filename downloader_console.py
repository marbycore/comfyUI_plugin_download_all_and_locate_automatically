import os
import sys
import json
import time
import requests

def format_size(bytes_num):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024:
            return f"{bytes_num:.1f}{unit}"
        bytes_num /= 1024
    return f"{bytes_num:.1f}TB"

def download_with_progress(url, dest_path, filename):
    print(f"\n  Downloading: {filename}")
    print(f"  To: {dest_path}")
    
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    try:
        # Use Range header to get real size from HuggingFace/redirects if needed
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        
        total = int(r.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        bar_width = 40
        
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):  # 1MB chunks
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    
                    elapsed = time.time() - start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0
                    
                    if total > 0:
                        pct = downloaded / total
                        filled = int(bar_width * pct)
                        bar = '█' * filled + '░' * (bar_width - filled)
                        eta = (total - downloaded) / speed if speed > 0 else 0
                        print(f"\r  [{bar}] {pct*100:.1f}% | {format_size(downloaded)}/{format_size(total)} | {format_size(speed)}/s | ETA: {eta:.0f}s", end='', flush=True)
                    else:
                        print(f"\r  Downloaded: {format_size(downloaded)} | {format_size(speed)}/s", end='', flush=True)
        
        print(f"\n  [OK] Successfully downloaded {filename}")
        return True
    except Exception as e:
        print(f"\n  [ERROR] Failed to download {filename}: {e}")
        if os.path.exists(dest_path):
            os.remove(dest_path)
        return False

def main():
    if len(sys.argv) < 2:
        print("Usage: downloader_console.py <pending_downloads_json>")
        return

    temp_file = sys.argv[1]
    if not os.path.exists(temp_file):
        print(f"Error: Temp file {temp_file} not found.")
        return

    with open(temp_file, 'r', encoding='utf-8') as f:
        missing_models = json.load(f)

    # In the extension context, we can find the models folder relative to this file
    # This file is in custom_nodes/comfyUI_plugin_extension/downloader_console.py
    # ComfyUI root is 2 levels up
    extension_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(extension_dir))
    models_root = os.path.join(base_dir, "models")


    print("="*60)
    print("  COMFYUI AUTO MODEL DOWNLOADER")
    print("  Developer: Marbycore")
    print("="*60)
    print(f"\n  Detected {len(missing_models)} missing models:")
    
    for m in missing_models:
        if m.get("url"):
            print(f"    [+] {m['filename']} -> models/{m['folder']}/")
        else:
            print(f"    [!] {m['filename']} -> No URL found (add it to custom_models.json)")
    
    downloadable = [m for m in missing_models if m.get("url")]
    
    if not downloadable:
        print("\n  No models with known URLs to download.")
        print("  Add URLs to custom_models.json inside the extension folder.")
        input("\n  Press Enter to close...")
        return


    print(f"\n  Total downloadable: {len(downloadable)}/{len(missing_models)}")
    print("\n  The models will be downloaded and placed automatically.")
    confirm = input("\n  Start download now? (Y/n): ").strip().lower()
    
    if confirm == 'n':
        print("  Download cancelled.")
    else:
        success_count = 0
        for m in downloadable:
            dest = os.path.join(models_root, m['folder'], m['filename'])
            if download_with_progress(m['url'], dest, m['filename']):
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"  DOWNLOAD SUMMARY: {success_count}/{len(downloadable)} succeeded")
        print("="*60)
        print("\n  Please restart ComfyUI and reload the workflow.")

    # Cleanup temp file
    try:
        os.remove(temp_file)
    except:
        pass
        
    input("\n  Press Enter to close this window...")


if __name__ == "__main__":
    main()
