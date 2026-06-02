"""Stub latent_preview module for standalone comfy_bridge."""


def prepare_callback(model, steps, x0_output_dict=None):
    """No-op callback."""
    def callback(step, x0, x, total_steps):
        if x0_output_dict is not None:
            x0_output_dict["x0"] = x0
    return callback


def set_preview_method(override: str = None):
    pass
