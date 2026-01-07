import os
import glob
import argparse
import numpy as np
import torch

from depth_anything_3.api import DepthAnything3


def run_da3_on_scene(scene_dir: str, model_name: str, suffix: str, device: str = "cuda") -> None:
    """Run DA3 on an IDR-style scene and save per-view depth.

    - scene_dir: path like data/gaussian-surfels-dtu-hf/scan106 or data/hope_video/scene_0000
    - model_name: e.g. "da3mono-large" (relative) or "da3metric-large" (metric)
    - suffix: will be appended to depth filename, e.g. "rel" -> *_rel_depth.npy, "metric" -> *_metric_depth.npy
    """
    image_dir = os.path.join(scene_dir, "image")
    assert os.path.isdir(image_dir), f"image dir not found: {image_dir}"

    img_paths = sorted(
        [
            os.path.join(image_dir, f)
            for f in os.listdir(image_dir)
            if f.lower().endswith((".png", ".jpg", ".jpeg"))
        ]
    )
    if not img_paths:
        raise RuntimeError(f"no images found in {image_dir}")

    print(f"[DA3] scene: {scene_dir}, model: {model_name}, images: {len(img_paths)}")

    model = DepthAnything3(model_name=model_name).to(device)
    model.eval()

    depth_dir = os.path.join(scene_dir, "depth")
    os.makedirs(depth_dir, exist_ok=True)

    # run in batches to avoid OOM
    batch_size = 4
    with torch.no_grad():
        for i in range(0, len(img_paths), batch_size):
            batch_paths = img_paths[i : i + batch_size]
            print(f"  batch {i} - {i + len(batch_paths) - 1}")

            pred = model.inference(
                image=batch_paths,
                process_res=504,
                process_res_method="upper_bound_resize",
                export_dir=None,
                export_format="mini_npz",
            )

            depths = pred.depth  # [N, H, W] float32
            assert depths.shape[0] == len(batch_paths)

            for p, d in zip(batch_paths, depths):
                base = os.path.splitext(os.path.basename(p))[0]
                out_path = os.path.join(depth_dir, f"{base}_{suffix}_depth.npy")
                np.save(out_path, d.astype(np.float32))

    print(f"[DA3] done: {scene_dir}, model: {model_name}, suffix: {suffix}")


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--scene", type=str, required=True, help="scene dir, e.g. data/gaussian-surfels-dtu-hf/scan106")
    parser.add_argument("--device", type=str, default="cuda")
    args = parser.parse_args()

    # relative depth (monocular)
    run_da3_on_scene(args.scene, model_name="da3mono-large", suffix="rel", device=args.device)
    # metric depth
    run_da3_on_scene(args.scene, model_name="da3metric-large", suffix="metric", device=args.device)


if __name__ == "__main__":
    main()
