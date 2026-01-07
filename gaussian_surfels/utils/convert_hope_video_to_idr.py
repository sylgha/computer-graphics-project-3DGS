import os
import json
import argparse
import random
import shutil

import numpy as np


def find_rgb_image(scene_dir: str, base: str) -> str:
    """Find the RGB image corresponding to a given JSON base name.

    HOPE-Video convention (see README):
    - 0000.json -> 0000_rgb.jpg (default)
    We also try a few common fallbacks.
    """
    candidates = [
        f"{base}_rgb.jpg",
        f"{base}_rgb.png",
        f"{base}.jpg",
        f"{base}.png",
    ]
    for name in candidates:
        path = os.path.join(scene_dir, name)
        if os.path.exists(path):
            return path
    raise FileNotFoundError(f"No RGB image found for base '{base}' in {scene_dir}")


def convert_scene(hope_scene_dir: str, out_scene_dir: str, num_frames: int, seed: int) -> None:
    os.makedirs(out_scene_dir, exist_ok=True)
    image_dir = os.path.join(out_scene_dir, "image")
    os.makedirs(image_dir, exist_ok=True)

    # List all annotation jsons in the HOPE-Video scene directory
    json_files = [
        os.path.join(hope_scene_dir, f)
        for f in os.listdir(hope_scene_dir)
        if f.endswith(".json")
    ]
    if not json_files:
        raise RuntimeError(f"No JSON files found in {hope_scene_dir}")

    json_files.sort()

    random.seed(seed)
    if len(json_files) > num_frames:
        selected_jsons = random.sample(json_files, num_frames)
    else:
        selected_jsons = json_files

    # Sort selected files to have a stable order for indexing 0..N-1
    selected_jsons.sort()

    world_mats = {}
    scale_mats = {}

    for idx, json_path in enumerate(selected_jsons):
        with open(json_path, "r") as f:
            data = json.load(f)

        cam = data["camera"]
        intrinsics = np.array(cam["intrinsics"], dtype=np.float32)  # 3x3
        extrinsics = np.array(cam["extrinsics"], dtype=np.float32)  # 4x4, world-to-camera

        # Projective matrix P = K [R|t]
        P = intrinsics @ extrinsics[:3, :4]

        world_mat = np.eye(4, dtype=np.float32)
        world_mat[:3, :4] = P
        scale_mat = np.eye(4, dtype=np.float32)

        world_mats[f"world_mat_{idx}"] = world_mat
        scale_mats[f"scale_mat_{idx}"] = scale_mat

        base = os.path.splitext(os.path.basename(json_path))[0]
        rgb_src = find_rgb_image(hope_scene_dir, base)

        # Rename frames to 0000.png, 0001.png, ... for this converted dataset
        img_name = f"{idx:04d}.png"
        img_dst = os.path.join(image_dir, img_name)

        # Use shutil.copyfile; if source is jpg it will remain jpg data on .png extension,
        # which is fine for imageio/PIL. For strict conversion, one could re-encode, but
        # that is unnecessary here.
        shutil.copyfile(rgb_src, img_dst)

    # Save cameras.npz in IDR-compatible format
    cameras_path = os.path.join(out_scene_dir, "cameras.npz")
    np.savez(cameras_path, **world_mats, **scale_mats)

    print(
        f"Converted {len(selected_jsons)} frames from '{hope_scene_dir}' "
        f"into '{out_scene_dir}'"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Convert HOPE-Video scenes to IDR-style dataset for gaussian_surfels."
    )

    script_dir = os.path.dirname(os.path.abspath(__file__))
    default_hope_root = os.path.abspath(
        os.path.join(script_dir, os.pardir, "hope-dataset", "hope_video")
    )
    default_out_root = os.path.abspath(os.path.join(script_dir, os.pardir, "data", "hope_video"))

    parser.add_argument(
        "--hope_root",
        type=str,
        default=default_hope_root,
        help="Root directory of HOPE-Video scenes (containing scene_0000, scene_0001, ...)",
    )
    parser.add_argument(
        "--out_root",
        type=str,
        default=default_out_root,
        help="Output root for converted IDR-style datasets.",
    )
    parser.add_argument(
        "--scenes",
        type=str,
        nargs="+",
        default=["scene_0000", "scene_0001"],
        help="Scene IDs to convert (directories under hope_root).",
    )
    parser.add_argument(
        "--num_frames",
        type=int,
        default=100,
        help="Maximum number of frames to sample per scene.",
    )
    parser.add_argument(
        "--seed",
        type=int,
        default=0,
        help="Random seed for frame sampling.",
    )

    args = parser.parse_args()

    for scene in args.scenes:
        hope_scene_dir = os.path.join(args.hope_root, scene)
        out_scene_dir = os.path.join(args.out_root, scene)

        if not os.path.isdir(hope_scene_dir):
            print(f"[WARN] Scene directory not found, skipping: {hope_scene_dir}")
            continue

        convert_scene(hope_scene_dir, out_scene_dir, args.num_frames, args.seed)


if __name__ == "__main__":
    main()
