"""Song Splitter – Auto Setup & Run (Demucs)
--------------------------------------------
Splits an input song into vocals, drums, bass, and other instruments.

Usage:
    python song_splitter.py song.mp3

Output:
    ./separated_stems/<song_name>/vocals.wav
    ./separated_stems/<song_name>/drums.wav
    ./separated_stems/<song_name>/bass.wav
    ./separated_stems/<song_name>/other.wav
"""

import importlib
import importlib.util
import os
import sys
import subprocess
from pathlib import Path
import shutil

# ---------- Utility functions ----------

def check_installed(package: str) -> bool:
    """Check if a Python package is installed (uses importlib)

    Accepts either top-level package name (e.g. 'torch') or module name.
    """
    try:
        return importlib.util.find_spec(package) is not None
    except Exception:
        return False

def install_package(package: str):
    """Install a package with pip"""
    print(f"📦 Installing {package} ...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", package])

def ensure_dependencies():
    """Ensure demucs, torch, and ffmpeg are installed"""
    # Demucs + Torch
    if not check_installed("demucs"):
        install_package("demucs")

    if not check_installed("torch"):
        print("📦 Installing PyTorch (CPU version)...")
        subprocess.check_call([sys.executable, "-m", "pip", "install", "torch", "--index-url", "https://download.pytorch.org/whl/cpu"])

    # FFmpeg
    if shutil.which("ffmpeg") is None:
        print("⚠ FFmpeg not found in PATH.")
        print("Please install FFmpeg manually:")
        print(" - Windows: choco install ffmpeg  (or download from ffmpeg.org)")
        print(" - Linux: sudo apt install ffmpeg")
        print(" - macOS: brew install ffmpeg")
        sys.exit(1)

# ---------- Main logic ----------

def separate_song(song_path: Path):
    """Run Demucs separation"""
    output_dir = Path("separated_stems")
    output_dir.mkdir(exist_ok=True)

    print(f"\n🎧 Splitting: {song_path.name}")
    cmd = [
        sys.executable, "-m", "demucs",
        "-n", "htdemucs",
        "-o", str(output_dir),
        str(song_path)
    ]

    # Run demucs and stream output
    try:
        process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True)
        for line in process.stdout:
            print(line, end="")
        process.wait()

        if process.returncode == 0:
            print(f"\n✅ Done! Separated stems saved in: {output_dir.resolve()}")
        else:
            print("\n❌ Error during Demucs run. Please check above logs.")
    except FileNotFoundError as e:
        print("\n❌ Failed to run demucs. Is it installed and available as a module?", e)
    except Exception as e:
        print("\n❌ Unexpected error while running demucs:", str(e))

# ---------- Entry point ----------

def main(argv=None):
    argv = argv or sys.argv
    if len(argv) < 2:
        print("Usage: python song_splitter.py <path_to_song.mp3>")
        return 1

    song_path = Path(argv[1])
    if not song_path.exists():
        print(f"❌ File not found: {song_path}")
        return 1

    ensure_dependencies()
    separate_song(song_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())