# ComfyUI Auto Model Downloader
**Desarrollado por [Marbycore](https://github.com/marbycore)**

[![ComfyUI](https://img.shields.io/badge/ComfyUI-Custom%20Node-blue)](https://github.com/comfyanonymous/ComfyUI)
[![Licencia: MIT](https://img.shields.io/badge/Licencia-MIT-green.svg)](LICENSE)
[![Plataforma](https://img.shields.io/badge/Plataforma-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)]()

> **Detecta y descarga automáticamente los modelos faltantes al abrir cualquier workflow de ComfyUI.**
> Sin configuración. Sin pasos manuales. Funciona con cualquier modelo que ComfyUI-Manager conozca.

---

## ✨ Cómo Funciona

1. Abres un workflow en ComfyUI
2. La extensión escanea todos los nodos buscando referencias a modelos
3. Verifica si cada archivo existe en tu instalación de ComfyUI
4. Si falta algún modelo → se abre automáticamente una ventana de consola
5. Confirmas y descarga todo con barra de progreso en tiempo real
6. Los archivos quedan en la carpeta correcta — reinicia ComfyUI, listo

### Ejemplo de consola
```
============================================================
  COMFYUI AUTO MODEL DOWNLOADER  |  Developer: Marbycore
============================================================

  Modelos faltantes detectados (3):
    [+] acestep_v1.5_turbo.safetensors  (4.46 GB)  -> diffusion_models/
    [+] ace_1.5_vae.safetensors         (321 MB)   -> vae/
    [!] mi_lora_custom.safetensors                 -> Sin URL conocida

  Total a descargar: 4.78 GB
  Descargar ahora? (S/n): _
```

---

## 🚀 Instalación

### Método 1 — ComfyUI Manager (Recomendado, 1 clic)

1. Abre ComfyUI en tu navegador
2. Haz clic en **Manager** → **Install via Git URL**
3. Pega la URL de abajo y haz clic en **Install**

```
https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically.git
```

4. Haz clic en **Restart** cuando se solicite
5. Listo ✅

---

### Método 2 — Git clone (Manual)

Abre una terminal dentro de la carpeta `custom_nodes` de tu ComfyUI y ejecuta:

```bash
# Windows (PowerShell)
cd C:\ruta\a\ComfyUI\custom_nodes
git clone https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically.git

# macOS / Linux
cd /ruta/a/ComfyUI/custom_nodes
git clone https://github.com/marbycore/comfyUI_plugin_download_all_and_locate_automatically.git
```

Luego reinicia ComfyUI.

---

### Método 3 — Descargar ZIP

1. Haz clic en el botón verde **Code** en esta página → **Download ZIP**
2. Extrae la carpeta dentro de `ComfyUI/custom_nodes/`
3. Renombra la carpeta extraída a `comfyUI_plugin_download_all_and_locate_automatically`
4. Reinicia ComfyUI

---

## ✅ Verificar la Instalación

Después de reiniciar ComfyUI, busca esta línea en la consola de inicio:

```
[AutoModelDownloader] v2.1 ready — Developer: Marbycore
```

Si la ves, la extensión está activa. Carga cualquier workflow para probarlo.

---

## ⚙️ Búsqueda Automática de URLs

La extensión encuentra las URLs de descarga automáticamente en este orden de prioridad:

| Prioridad | Requisito | Notas |
|-------------|-------|
| ComfyUI | Cualquier versión reciente |
| Python 3.9+ | Incluido con ComfyUI |
| `requests` | Pre-instalado con ComfyUI |
| **aria2c** | **(Muy Recomendado)** para descargas 10 veces más rápidas (multi-conexión) |
| ComfyUI-Manager | Opcional pero recomendado para máxima cobertura de URLs |

---

### ⚡ Acelerando las descargas (Aria2c)

Para descargas ultra-rápidas (16 conexiones simultáneas), instala `aria2c` en tu sistema:

- **Windows**: Abre PowerShell como Admin y ejecuta: `winget install aria2.aria2`
- **Linux**: `sudo apt install aria2`
- **macOS**: `brew install aria2`

La extensión detectará automáticamente `aria2c` y lo usará si está disponible.

| Prioridad | Fuente | Cobertura |
|-----------|--------|-----------|
| 1 | `model_registry.py` local | Cache curado (ACE-Step, Wan 2.2, SeedVR2…) |
| 2 | BD local de ComfyUI-Manager | Miles de modelos de la comunidad (offline, instantáneo) |
| 3 | BD online de ComfyUI-Manager | Lista completa actualizada, obtenida en el primer uso |

**Nunca necesitas configurar URLs manualmente** — si un modelo está en la base de datos de ComfyUI-Manager, se encontrará automáticamente.

---

## 📁 Agregar URLs de Modelos Personalizados

Si un modelo muestra `[!] Sin URL conocida`, crea un archivo `custom_models.json` dentro de la carpeta de la extensión:

```json
{
  "mi_modelo.safetensors": {
    "url": "https://huggingface.co/tu-org/tu-repo/resolve/main/mi_modelo.safetensors",
    "folder": "checkpoints"
  }
}
```

Valores de carpeta soportados:

| Valor | Carpeta de ComfyUI |
|-------|-------------------|
| `checkpoints` | `models/checkpoints/` |
| `diffusion_models` | `models/diffusion_models/` |
| `vae` | `models/vae/` |
| `text_encoders` | `models/text_encoders/` |
| `loras` | `models/loras/` |
| `controlnet` | `models/controlnet/` |
| `upscale_models` | `models/upscale_models/` |
| `clip_vision` | `models/clip_vision/` |

---

## 📄 Licencia

MIT — ver [LICENSE](LICENSE)
