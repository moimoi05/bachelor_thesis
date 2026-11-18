"""Export the two editable RC-Free diagrams using draw.io Desktop."""
import argparse
import os
from pathlib import Path
import shutil
import subprocess
import sys

import pymupdf
from PIL import Image

SOURCE = Path(__file__).resolve().parent
IMAGE_DIR = SOURCE.parent / "image"
DIAGRAMS = ("final-pipeline", "master-pipeline")


def resolve_drawio(explicit=None):
    candidate = explicit or os.environ.get("THESIS_DRAWIO") or shutil.which("draw.io")
    if not candidate:
        raise FileNotFoundError("Set THESIS_DRAWIO or supply --drawio with the draw.io Desktop executable.")
    return candidate


def export(name, drawio):
    diagram = SOURCE / f"{name}.drawio"
    IMAGE_DIR.mkdir(exist_ok=True)
    # Draw.io's PDF export remains vector; create a 300 dpi preview from that exact PDF.
    for extension in ("svg", "pdf"):
        target = IMAGE_DIR / f"{name}.{extension}"
        command = [
            str(drawio), "--export", "--disable-gpu", "--format", extension,
            "--embed-diagram", "--crop", "--border", "10",
            "--output", str(target), str(diagram),
        ]
        flags = subprocess.CREATE_NO_WINDOW if sys.platform == "win32" else 0
        completed = subprocess.run(command, check=True, capture_output=True, text=True,
                                   creationflags=flags, timeout=60)
        if not target.is_file() or target.stat().st_size == 0:
            raise RuntimeError(f"Missing export {target}: {completed.stderr}")
    with pymupdf.open(IMAGE_DIR / f"{name}.pdf") as pdf:
        page = pdf[0]
        pixmap = page.get_pixmap(dpi=300, alpha=False)
        image = Image.frombytes("RGB", (pixmap.width, pixmap.height), pixmap.samples)
        image.save(IMAGE_DIR / f"{name}.png", dpi=(300, 300))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--drawio", type=Path)
    parser.add_argument("--figure", choices=DIAGRAMS)
    args = parser.parse_args()
    drawio = resolve_drawio(args.drawio)
    for name in (args.figure,) if args.figure else DIAGRAMS:
        export(name, drawio)


if __name__ == "__main__":
    main()
