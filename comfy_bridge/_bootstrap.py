import os, sys
# Make comfy_bridge self-contained
_BRIDGE_DIR = os.path.dirname(os.path.abspath(__file__))
if _BRIDGE_DIR not in sys.path:
    sys.path.insert(0, _BRIDGE_DIR)
_CUSTOM = os.path.join(_BRIDGE_DIR, "custom_nodes")
if _CUSTOM not in sys.path:
    sys.path.insert(0, _CUSTOM)

# Point models directory to comfy_bridge/models (self-contained)
os.environ["COMFYUI_MODELS_DIR"] = os.path.join(_BRIDGE_DIR, "models")
