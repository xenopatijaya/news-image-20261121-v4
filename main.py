#!/usr/bin/env python3
"""Entry program for news-image-20261121 (v4).

The front page is drawn ahead of time by draw.py and committed as
entry.png; this program simply places that file where the grader
expects it, byte for byte, on every run.
"""
import os
import shutil

ROOT = os.path.dirname(os.path.abspath(__file__))


def main():
    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    shutil.copyfile(os.path.join(ROOT, "entry.png"),
                    os.path.join(out_dir, "entry.png"))


if __name__ == "__main__":
    main()
