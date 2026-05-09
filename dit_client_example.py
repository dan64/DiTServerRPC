"""
-------------------------------------------------------------------------------
Author: Dan64
Date: 2026-01-14
-------------------------------------------------------------------------------
DiT Colorize RPC Client — example
Connects to a running dit_rpc_server instance and colorizes the sample image
assets/santa_bw.png, saving the result as assets/santa_colorized.png.

Usage:
    python dit_client_example.py [--host HOST] [--port PORT]
                                 [--pipeline-config CONFIG.json]
                                 [--prompt "..."]

If --pipeline-config is given the client will load the pipeline on the server
before colorizing; otherwise the pipeline must already be loaded.
-------------------------------------------------------------------------------
"""

import argparse
import io
import json
import sys
import time
import xmlrpc.client
from pathlib import Path

from PIL import Image

# ---------------------------------------------------------------------------
# Helpers — same convention as the server
# ---------------------------------------------------------------------------

def _pil_to_bytes(img: Image.Image) -> bytes:
    """Serialize a PIL Image to raw PNG bytes."""
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    return buf.getvalue()


def _bytes_to_pil(data) -> Image.Image:
    """Deserialize raw PNG bytes (or xmlrpc.client.Binary) into a PIL Image."""
    raw = data.data if hasattr(data, "data") else data
    return Image.open(io.BytesIO(raw)).convert("RGB")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main():
    parser = argparse.ArgumentParser(
        description="DiT Colorize RPC Client — example",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("--host", default="127.0.0.1",
                        help="Server host")
    parser.add_argument("--port", type=int, default=8765,
                        help="Server port")
    parser.add_argument("--pipeline-config", default="",
                        metavar="CONFIG.json",
                        help="Path to a JSON pipeline config file. "
                             "When provided the client calls load_pipeline() "
                             "before colorizing; omit if the server already "
                             "has the pipeline loaded.")
    parser.add_argument("--prompt",
                        default="Colorize this photo, natural skin tones, "
                                "vibrant environment. Maintain consistency "
                                "and details.",
                        help="Text prompt sent to the colorization model")
    parser.add_argument("--img-size", type=int, default=0,
                        help="Maximum long side in pixels before inference "
                             "(0 = keep original size)")
    parser.add_argument("--steps", type=int, default=2,
                        help="Number of inference steps")
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Paths
    # ------------------------------------------------------------------
    script_dir  = Path(__file__).parent.resolve()
    input_path  = script_dir / "assets" / "santa_bw.png"
    output_path = script_dir / "assets" / "santa_colorized.png"

    if not input_path.exists():
        print(f"[ERROR] Input image not found: {input_path}")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Connect
    # ------------------------------------------------------------------
    server_url = f"http://{args.host}:{args.port}/"
    print(f"[INFO] Connecting to {server_url} ...")
    proxy = xmlrpc.client.ServerProxy(server_url, use_builtin_types=True)

    try:
        response = proxy.ping()
    except ConnectionRefusedError:
        print(f"[ERROR] Could not reach the server at {server_url}.")
        print("        Make sure dit_rpc_server.py is running.")
        sys.exit(1)

    if response != "pong":
        print(f"[ERROR] Unexpected ping response: {response!r}")
        sys.exit(1)

    print("[INFO] Server is reachable.")

    # ------------------------------------------------------------------
    # Optional: load pipeline from config file
    # ------------------------------------------------------------------
    if args.pipeline_config:
        config_path = Path(args.pipeline_config)
        if not config_path.is_file():
            print(f"[ERROR] Config file not found: {config_path}")
            sys.exit(1)

        with config_path.open(encoding="utf-8") as fh:
            cfg = json.load(fh)

        print(f"[INFO] Loading pipeline from: {config_path.name} ...")
        result = proxy.load_pipeline(
            cfg["model_name"],
            cfg["model_precision"],
            cfg["model_rank"],
            cfg["model_inference_steps"],
            cfg.get("cache_dir", ""),
            cfg.get("full_model_path", ""),
        )
        if not result["ok"]:
            print(f"[ERROR] load_pipeline failed: {result['msg']}")
            sys.exit(1)
        print("[INFO] Pipeline loaded successfully.")

    elif not proxy.is_pipeline_loaded():
        print("[ERROR] The pipeline is not loaded on the server.")
        print("        Either pass --pipeline-config or start the server")
        print("        with --load-pipeline --pipeline-config CONFIG.json.")
        sys.exit(1)

    # ------------------------------------------------------------------
    # Read input image and send to server for colorization
    # ------------------------------------------------------------------
    print(f"[INFO] Reading input image: {input_path}")
    img_in  = Image.open(input_path).convert("RGB")
    img_bytes = _pil_to_bytes(img_in)

    print(f"[INFO] Colorizing ({img_in.width}x{img_in.height} px) ...")
    t0 = time.perf_counter()
    result = proxy.colorize_frame(
        img_bytes,
        args.prompt,
        args.img_size,
        args.steps,
    )
    wall_time = time.perf_counter() - t0

    if not result["ok"]:
        print(f"[ERROR] colorize_frame failed: {result['msg']}")
        sys.exit(1)

    if result["skipped"]:
        print("[WARN] Image was too dark to colorize — output is unchanged.")
    else:
        print(f"[INFO] Inference time : {result['elapsed']:.2f}s")
        print(f"[INFO] Round-trip time: {wall_time:.2f}s")

    # ------------------------------------------------------------------
    # Save result
    # ------------------------------------------------------------------
    img_out = _bytes_to_pil(result["data"])
    output_path.parent.mkdir(parents=True, exist_ok=True)
    img_out.save(output_path)
    print(f"[INFO] Saved colorized image to: {output_path}")


if __name__ == "__main__":
    main()
