import os
import time
import mimetypes
import logging
from typing import Literal, List
from collections.abc import Collection

from comfy.cli_args import args

supported_pt_extensions: set[str] = {'.ckpt', '.pt', '.pt2', '.bin', '.pth', '.safetensors', '.pkl', '.sft'}

folder_names_and_paths: dict[str, tuple[list[str], set[str]]] = {}

# --base-directory
if args.base_directory:
    base_path = os.path.abspath(args.base_directory)
elif os.environ.get("COMFYUI_MODELS_DIR"):
    base_path = os.path.dirname(os.environ["COMFYUI_MODELS_DIR"])
else:
    base_path = os.path.dirname(os.path.realpath(__file__))

models_dir = os.path.join(base_path, "models")
folder_names_and_paths["checkpoints"] = ([os.path.join(models_dir, "checkpoints")], supported_pt_extensions)
folder_names_and_paths["configs"] = ([os.path.join(models_dir, "configs")], [".yaml"])
folder_names_and_paths["loras"] = ([os.path.join(models_dir, "loras")], supported_pt_extensions)
folder_names_and_paths["vae"] = ([os.path.join(models_dir, "vae")], supported_pt_extensions)
folder_names_and_paths["text_encoders"] = ([os.path.join(models_dir, "text_encoders"), os.path.join(models_dir, "clip")], supported_pt_extensions)
folder_names_and_paths["diffusion_models"] = ([os.path.join(models_dir, "unet"), os.path.join(models_dir, "diffusion_models")], supported_pt_extensions)
folder_names_and_paths["clip_vision"] = ([os.path.join(models_dir, "clip_vision")], supported_pt_extensions)
folder_names_and_paths["style_models"] = ([os.path.join(models_dir, "style_models")], supported_pt_extensions)
folder_names_and_paths["embeddings"] = ([os.path.join(models_dir, "embeddings")], supported_pt_extensions)
folder_names_and_paths["diffusers"] = ([os.path.join(models_dir, "diffusers")], ["folder"])
folder_names_and_paths["vae_approx"] = ([os.path.join(models_dir, "vae_approx")], supported_pt_extensions)
folder_names_and_paths["controlnet"] = ([os.path.join(models_dir, "controlnet"), os.path.join(models_dir, "t2i_adapter")], supported_pt_extensions)
folder_names_and_paths["gligen"] = ([os.path.join(models_dir, "gligen")], supported_pt_extensions)
folder_names_and_paths["upscale_models"] = ([os.path.join(models_dir, "upscale_models")], supported_pt_extensions)
folder_names_and_paths["latent_upscale_models"] = ([os.path.join(models_dir, "latent_upscale_models")], supported_pt_extensions)
folder_names_and_paths["custom_nodes"] = ([os.path.join(base_path, "custom_nodes")], set())
folder_names_and_paths["hypernetworks"] = ([os.path.join(models_dir, "hypernetworks")], supported_pt_extensions)
folder_names_and_paths["photomaker"] = ([os.path.join(models_dir, "photomaker")], supported_pt_extensions)
folder_names_and_paths["classifiers"] = ([os.path.join(models_dir, "classifiers")], {""})
folder_names_and_paths["model_patches"] = ([os.path.join(models_dir, "model_patches")], supported_pt_extensions)
folder_names_and_paths["audio_encoders"] = ([os.path.join(models_dir, "audio_encoders")], supported_pt_extensions)
folder_names_and_paths["background_removal"] = ([os.path.join(models_dir, "background_removal")], supported_pt_extensions)
folder_names_and_paths["frame_interpolation"] = ([os.path.join(models_dir, "frame_interpolation")], supported_pt_extensions)
folder_names_and_paths["geometry_estimation"] = ([os.path.join(models_dir, "geometry_estimation")], supported_pt_extensions)
folder_names_and_paths["optical_flow"] = ([os.path.join(models_dir, "optical_flow")], supported_pt_extensions)
folder_names_and_paths["detection"] = ([os.path.join(models_dir, "detection")], supported_pt_extensions)

output_directory = os.path.join(base_path, "output")
temp_directory = os.path.join(base_path, "temp")
input_directory = os.path.join(base_path, "input")
user_directory = os.path.join(base_path, "user")

filename_list_cache: dict[str, tuple[list[str], dict[str, float], float]] = {}

class CacheHelper:
    def __init__(self):
        self.cache: dict[str, tuple[list[str], dict[str, float], float]] = {}
        self.active = False
    def get(self, key: str, default=None) -> tuple[list[str], dict[str, float], float]:
        if not self.active: return default
        return self.cache.get(key, default)
    def set(self, key: str, value: tuple[list[str], dict[str, float], float]) -> None:
        if self.active: self.cache[key] = value
    def clear(self): self.cache.clear()
    def __enter__(self): self.active = True; return self
    def __exit__(self, *a): self.active = False; self.clear()

cache_helper = CacheHelper()
extension_mimetypes_cache = {"webp": "image", "fbx": "model"}

def map_legacy(folder_name: str) -> str:
    return {"unet": "diffusion_models", "clip": "text_encoders"}.get(folder_name, folder_name)

if not os.path.exists(input_directory):
    try: os.makedirs(input_directory)
    except: logging.error("Failed to create input directory")

def set_output_directory(d): global output_directory; output_directory = d
def set_temp_directory(d): global temp_directory; temp_directory = d
def set_input_directory(d): global input_directory; input_directory = d
def get_output_directory() -> str: return output_directory
def get_temp_directory() -> str: return temp_directory
def get_input_directory() -> str: return input_directory
def get_user_directory() -> str: return user_directory
def set_user_directory(d): global user_directory; user_directory = d

SYSTEM_USER_PREFIX = "__"

def get_system_user_directory(name: str = "system") -> str:
    if not name or not isinstance(name, str): raise ValueError("System user name cannot be empty")
    if not name.replace("_", "").isalnum(): raise ValueError(f"Invalid system user name: '{name}'")
    if name.startswith("_"): raise ValueError("System user name should not start with underscore")
    return os.path.join(get_user_directory(), f"{SYSTEM_USER_PREFIX}{name}")

def get_public_user_directory(user_id: str) -> str | None:
    if not user_id or not isinstance(user_id, str): return None
    if user_id.startswith(SYSTEM_USER_PREFIX): return None
    return os.path.join(get_user_directory(), user_id)

def get_directory_by_type(type_name: str) -> str | None:
    if type_name == "output": return get_output_directory()
    if type_name == "temp": return get_temp_directory()
    if type_name == "input": return get_input_directory()
    return None

def add_supported_extensions(exts: set[str], supported: set[str]) -> set[str]:
    return exts | supported

def get_full_path(folder_name: str, filename: str) -> str | None:
    folder_name = map_legacy(folder_name)
    if folder_name not in folder_names_and_paths: return None
    folders, exts = folder_names_and_paths[folder_name]
    ext = os.path.splitext(filename)[1].lower()
    if ext not in exts and "" not in exts and "*" not in exts: return None
    for folder in folders:
        fp = os.path.join(folder, filename)
        if os.path.isfile(fp): return fp
    return None

def get_full_path_or_raise(folder_name: str, filename: str) -> str:
    fp = get_full_path(folder_name, filename)
    if fp is None:
        raise FileNotFoundError(f"Model in folder '{folder_name}' with filename '{filename}' not found.")
    return fp

def get_filename_list(folder_name: str) -> list[str]:
    folder_name = map_legacy(folder_name)
    if folder_name not in folder_names_and_paths: return []
    folders, exts = folder_names_and_paths[folder_name]
    files = set()
    for folder in folders:
        if not os.path.isdir(folder): continue
        for f in os.listdir(folder):
            if f.endswith(".disabled"): continue
            ext = os.path.splitext(f)[1].lower()
            if ext in exts or "" in exts or "*" in exts:
                files.add(f)
    return sorted(files)

def get_folder_paths(folder_name: str) -> list[str]:
    folder_name = map_legacy(folder_name)
    if folder_name not in folder_names_and_paths: return []
    return folder_names_and_paths[folder_name][0][:]
