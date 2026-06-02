"""Minimal cli_args stub for standalone comfy_bridge."""
import enum

class PerformanceFeature(enum.Enum):
    Fp16Accumulation = "fp16_accumulation"
    Fp8MatrixMultiplication = "fp8_matrix_mult"
    CublasOps = "cublas_ops"
    AutoTune = "autotune"

class LatentPreviewMethod(enum.Enum):
    NoPreviews = "none"
    Auto = "auto"
    Latent2RGB = "latent2rgb"
    TAESD = "taesd"

class _Args:
    base_directory = None
    default_device = None
    cuda_device = None
    enable_triton_backend = False
    highvram = False
    normalvram = False
    lowvram = False
    novram = False
    cpu = False
    gpu_only = False
    disable_dynamic_vram = False
    enable_dynamic_vram = False
    fast = set()
    deterministic = False
    directml = None
    disable_xformers = False
    use_pytorch_cross_attention = False
    use_split_cross_attention = False
    use_quad_cross_attention = False
    async_offload = None
    disable_async_offload = False
    disable_pinned_memory = False
    use_sage_attention = False
    use_flash_attention = False
    force_upcast_attention = False
    max_upload_size = 100  # MB
    disable_metadata = False
    verbose = 'INFO'
    feature_flag = []  # empty list for feature flags
    preview_method = LatentPreviewMethod.NoPreviews  # default
    def __getattr__(self, name):
        if name.startswith('_'):
            raise AttributeError(name)
        return None

args = _Args()
