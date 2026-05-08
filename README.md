# ComfyUI Auto Model Downloader
**Developer: [Marbycore](https://github.com/marbycore)**

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()

> **Automatically detects and downloads missing models when you open any ComfyUI workflow.**
> Zero configuration. Zero manual steps. Works with any model ComfyUI-Manager knows about.

---

## ✨ How It Works

1. You open a workflow in ComfyUI
2. The extension scans all nodes for model references
3. It checks whether each file exists in your ComfyUI installation
4. If any model is missing → a console window opens automatically
5. You confirm and it downloads everything with a real-time progress bar
6. Files land in the correct folder — restart ComfyUI, you are ready

### Console output example
```
============================================================
  COMFYUI AUTO MODEL DOWNLOADER  |  Developer: Marbycore
============================================================

  Detected 3 missing models:
    [+] acestep_v1.5_turbo.safetensors  (4.46 GB)  -> diffusion_models/
    [+] ace_1.5_vae.safetensors         (321 MB)   -> vae/
    [!] my_custom_lora.safetensors                 -> No URL found

  Total to download: 4.78 GB
  Start download now? (Y/n): _
```

---

## 🚀 Installation

### Method 1 — ComfyUI Manager (Recommended, 1 click)

1. Open ComfyUI in your browser
2. Click **Manager** → **Install via Git URL**
3. Paste the URL below and click **Install**

```
https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically.git
```

4. Click **Restart** when prompted
5. Done ✅

---

### Method 2 — Git clone (Manual)

Open a terminal inside your ComfyUI `custom_nodes` folder and run:

```bash
# Windows (PowerShell)
cd C:\path\to\ComfyUI\custom_nodes
git clone https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically.git

# macOS / Linux
cd /path/to/ComfyUI/custom_nodes
git clone https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically.git
```

Then restart ComfyUI.

---

### Method 3 — Download ZIP

1. Click the green **Code** button on this page → **Download ZIP**
2. Extract the folder into `ComfyUI/custom_nodes/`
3. Rename the extracted folder to `comfyUI_plugin_download_all_and_locate_automatically`
4. Restart ComfyUI

---

## ✅ Verify Installation

After restarting ComfyUI, look for this line in the startup console:

```
[AutoModelDownloader] v2.1 ready — Developer: Marbycore
```

If you see it, the extension is active. Load any workflow to test it.

---

## ⚙️ URL Auto-Discovery

The extension finds download URLs automatically in this priority order:

| Priority | Source | Coverage |
|----------|--------|----------|
| 1 | Local `model_registry.py` | Curated fast cache (ACE-Step, Wan 2.2, SeedVR2…) |
| 2 | ComfyUI-Manager local DB | Thousands of community models (offline, instant) |
| 3 | ComfyUI-Manager online DB | Full updated list fetched on first use |

**You never need to configure URLs manually** — if a model is in the ComfyUI-Manager database, it will be found automatically.

---

## 📁 Adding Custom Model URLs

If a model shows `[!] No URL found`, create a `custom_models.json` file inside the extension folder:

```json
{
  "my_model.safetensors": {
    "url": "https://huggingface.co/your-org/your-repo/resolve/main/my_model.safetensors",
    "folder": "checkpoints"
  }
}
```

Supported folder values:

| Value | ComfyUI folder |
|-------|----------------|
| `checkpoints` | `models/checkpoints/` |
| `diffusion_models` | `models/diffusion_models/` |
| `vae` | `models/vae/` |
| `text_encoders` | `models/text_encoders/` |
| `loras` | `models/loras/` |
| `controlnet` | `models/controlnet/` |
| `upscale_models` | `models/upscale_models/` |
| `clip_vision` | `models/clip_vision/` |

---

## 📋 Requirements

| Requirement | Notes |
|-------------|-------|
| ComfyUI | Any recent version |
| Python 3.9+ | Included with ComfyUI |
| `requests` | Pre-installed with ComfyUI |
| ComfyUI-Manager | Optional but recommended for maximum URL coverage |

---

## 🔒 Privacy

- No telemetry, no analytics, no external calls except to download the files you approve
- Downloads go directly from HuggingFace or the source URL to your machine
- Source code is fully readable and auditable

---

## 🤝 Contributing

Pull requests are welcome. To add a model to the built-in registry:

1. Fork the repository
2. Add an entry to `model_registry.py`
3. Submit a PR with the model name, verified URL, and correct folder

---

## 📄 License

MIT — see [LICENSE](LICENSE)
