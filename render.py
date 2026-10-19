"""Render the Physics Club reels.

    python render.py                 # all scenes, final 1080x1920 @ 30 fps
    python render.py --preview       # all scenes, quick 540x960 @ 15 fps
    python render.py pendulum waves  # only some scenes

Finished videos (plus .srt subtitles for narrated reels) are copied to
exports/ (finals) or exports/preview/.
"""

import argparse
import os
import shutil
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent

# name: (file, scene class, timestamp in seconds of a good cover frame)
SCENES = {
    "projectile": ("projectile.py", "ProjectileMotion", 64),
    "pendulum": ("pendulum.py", "Pendulum", 17),
    "waves": ("waves.py", "WaveInterference", 12),
    "kepler": ("kepler.py", "KeplerSecondLaw", 27),
    "electric_field": ("electric_field.py", "ElectricField", 16.5),
}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("scenes", nargs="*", help=f"any of: {', '.join(SCENES)} (default: all)")
    ap.add_argument("--preview", action="store_true", help="half resolution, 15 fps")
    ap.add_argument("--cover", action="store_true", help="also save a cover image (PNG)")
    args = ap.parse_args()
    unknown = set(args.scenes) - set(SCENES)
    if unknown:
        ap.error(f"unknown scene(s): {', '.join(sorted(unknown))}")

    res, fps = ("540,960", 15) if args.preview else ("1080,1920", 30)
    out_dir = ROOT / "exports" / ("preview" if args.preview else "")
    out_dir.mkdir(parents=True, exist_ok=True)
    env = {**os.environ, "PYTHONPATH": str(ROOT)}

    for name in args.scenes or SCENES:
        file, cls, cover_at = SCENES[name]
        cmd = [sys.executable, "-m", "manim", "render", "--config_file", str(ROOT / "manim.cfg"),
               "-r", res, "--fps", str(fps), "--media_dir", str(ROOT / "media"),
               "-o", name, str(ROOT / "scenes" / file), cls]
        print(f"\n=== {name} ===")
        subprocess.run(cmd, check=True, env=env, cwd=ROOT)
        height = res.split(",")[1]
        video = ROOT / "media" / "videos" / Path(file).stem / f"{height}p{fps}" / f"{name}.mp4"
        shutil.copy(video, out_dir / f"{name}.mp4")
        if video.with_suffix(".srt").exists():  # subtitles, written for narrated reels
            shutil.copy(video.with_suffix(".srt"), out_dir / f"{name}.srt")
        if args.cover:
            subprocess.run(["ffmpeg", "-v", "error", "-y", "-ss", str(cover_at), "-i", str(video),
                            "-frames:v", "1", str(out_dir / f"{name}_cover.png")], check=True)
        print(f"-> {out_dir / f'{name}.mp4'}")


if __name__ == "__main__":
    main()
