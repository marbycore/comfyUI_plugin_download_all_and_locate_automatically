# Model Registry for ComfyUI Auto-Downloader
# Add official/verified models here.

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
    "qwen_0.6b_ace15.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/text_encoders/qwen_0.6b_ace15.safetensors",
        "folder": "text_encoders"
    },
    "qwen_4b_ace15.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/ace_step_1.5_ComfyUI_files/resolve/main/split_files/text_encoders/qwen_4b_ace15.safetensors",
        "folder": "text_encoders"
    },
    # Wan 2.2
    "wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_high_noise_14B_fp8_scaled.safetensors",
        "folder": "diffusion_models"
    },
    "wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/diffusion_models/wan2.2_i2v_low_noise_14B_fp8_scaled.safetensors",
        "folder": "diffusion_models"
    },
    "wan_2.1_vae.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/Wan_2.2_ComfyUI_Repackaged/resolve/main/split_files/vae/wan_2.1_vae.safetensors",
        "folder": "vae"
    },
    "umt5_xxl_fp8_e4m3fn_scaled.safetensors": {
        "url": "https://huggingface.co/Comfy-Org/Wan_2.1_ComfyUI_repackaged/resolve/main/split_files/text_encoders/umt5_xxl_fp8_e4m3fn_scaled.safetensors",
        "folder": "text_encoders"
    },
    # SeedVR2
    "seedvr2_ema_3b_fp8_e4m3fn.safetensors": {
        "url": "https://huggingface.co/ByteDance/SeedVR2/resolve/main/seedvr2_ema_3b_fp8_e4m3fn.safetensors",
        "folder": "SEEDVR2"
    },
    "ema_vae_fp16.safetensors": {
        "url": "https://huggingface.co/ByteDance/SeedVR2/resolve/main/ema_vae_fp16.safetensors",
        "folder": "SEEDVR2"
    },
}
