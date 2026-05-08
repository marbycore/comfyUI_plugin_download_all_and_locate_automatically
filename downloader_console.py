import os
import sys
import json
import time
import requests
import subprocess
import shutil

# Developer: Marbycore
# Optimized Downloader with Aria2c support for ultra-fast downloads

def format_size(bytes_num):
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_num < 1024:
            return f"{bytes_num:.1f}{unit}"
        bytes_num /= 1024
    return f"{bytes_num:.1f}TB"

def is_aria2_available():
    return shutil.which("aria2c") is not None

def download_with_aria2(url, dest_path, filename):
    """Downloads using aria2c for maximum speed (multi-connection)."""
    print(f"\n  [ARIA2] Downloading: {filename}")
    
    folder = os.path.dirname(dest_path)
    os.makedirs(folder, exist_ok=True)
    
    cmd = [
        "aria2c",
        "-x", "16",       # 16 connections per server
        "-s", "16",       # Split file into 16 parts
        "-k", "1M",       # 1MB chunks
        "--console-log-level=warn",
        "--summary-interval=1",
        "--file-allocation=none", # Faster start on some systems
        url,
        "-d", folder,
        "-o", filename
    ]
    
    try:
        # Run aria2c and inherit the console output for progress
        result = subprocess.run(cmd)
        return result.returncode == 0
    except Exception as e:
        print(f"  [ARIA2 ERROR] {e}")
        return False

def download_with_requests(url, dest_path, filename):
    """Standard fallback downloader using requests."""
    print(f"\n  [Standard] Downloading: {filename}")
    os.makedirs(os.path.dirname(dest_path), exist_ok=True)
    
    try:
        r = requests.get(url, stream=True, timeout=30)
        r.raise_for_status()
        total = int(r.headers.get('content-length', 0))
        downloaded = 0
        start_time = time.time()
        
        with open(dest_path, 'wb') as f:
            for chunk in r.iter_content(chunk_size=1024*1024):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    elapsed = time.time() - start_time
                    speed = downloaded / elapsed if elapsed > 0 else 0
                    if total > 0:
                        pct = (downloaded / total) * 100
                        print(f"\r  Progress: {pct:.1f}% | {format_size(downloaded)}/{format_size(total)} | {format_size(speed)}/s", end='', flush=True)
        print(f"\n  [OK] Done.")
        return True
    except Exception as e:
        print(f"\n  [ERROR] {e}")
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

    extension_dir = os.path.dirname(os.path.abspath(__file__))
    base_dir = os.path.dirname(os.path.dirname(extension_dir))
    models_root = os.path.join(base_dir, "models")

    print("="*60)
    print("  COMFYUI AUTO MODEL DOWNLOADER | Developer: Marbycore")
    print("="*60)
    
    has_aria2 = is_aria2_available()
    print(f"\n  Download Engine: {'[ARIA2C] (High Speed)' if has_aria2 else '[REQUESTS] (Standard)'}")
    print(f"  Detected {len(missing_models)} missing models:\n")
    
    for m in missing_models:
        dest_path = os.path.join(models_root, m['folder'], m['filename'])
        if m.get("url"):
            print(f"  [+] {m['filename']} ({m.get('_source', 'Auto')})")
            print(f"      Save to: {dest_path}")
        else:
            print(f"  [!] {m['filename']} (No URL found)")
        print()
    
    downloadable = [m for m in missing_models if m.get("url")]
    
    if not downloadable:
        print("  Nothing to download automatically.")
        input("\n  Press Enter to close...")
        return

    confirm = input(f"\n  Start downloading {len(downloadable)} models? (Y/n): ").strip().lower()
    if confirm == 'n':
        print("  Cancelled.")
    else:
        success_count = 0
        for m in downloadable:
            dest = os.path.join(models_root, m['folder'], m['filename'])
            
            success = False
            if has_aria2:
                success = download_with_aria2(m['url'], dest, m['filename'])
            
            if not success: # Fallback to requests if aria2 fails or is missing
                success = download_with_requests(m['url'], dest, m['filename'])
                
            if success:
                success_count += 1
        
        print(f"\n{'='*60}")
        print(f"  SUMMARY: {success_count}/{len(downloadable)} models downloaded.")
        print("="*60)
        print("\n  Please restart ComfyUI or refresh to use the new models.")

    try:
        os.remove(temp_file)
    except:
        pass
    input("\n  Press Enter to close window...")

if __name__ == "__main__":
    main()
