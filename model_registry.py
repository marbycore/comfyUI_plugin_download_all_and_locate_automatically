# Model Registry for ComfyUI Auto-Downloader
# Developer: Marbycore
# This registry is only for priority overrides or models not in Manager DB.
# Most models are found automatically via ComfyUI-Manager's database.

BUILTIN_REGISTRY = {
    # ACE Step 1.5 (Comfy-Org public mirror)
    "acestep_v1.5_turbo.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/diffusion_models/acestep_v1.5_turbo.safetensors",
        "folder": "diffusion_models"
    },
    "ace_1.5_vae.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/vae/ace_1.5_vae.safetensors",
        "folder": "vae"
    },
    # Wan 2.2
    "wan2.1_t2v_1.3b_bf16.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/Wan2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_t2v_1.3b_bf16.safetensors",
        "folder": "diffusion_models"
    },
    "wan2.1_i2v_720p_480p_7b_bf16.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/Wan2.1_ComfyUI_repackaged/resolve/main/split_files/diffusion_models/wan2.1_i2v_720p_480p_7b_bf16.safetensors",
        "folder": "diffusion_models"
    },
    # Stable Audio (Comfy-Org Mirror - No Auth required)
    "stable-audio-open-1.0.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/stable-audio-open-1.0_repackaged/resolve/main/stable-audio-open-1.0.safetensors",
        "folder": "checkpoints"
    },


    "t5-base.safetensors": {
        "url": "https://huggingface.co/google-t5/t5-base/resolve/main/model.safetensors",
        "folder": "clip"
    },
}

