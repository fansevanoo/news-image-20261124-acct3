#!/usr/bin/env python3
"""news-image-20261124 acct3 (fansevanoo) — copy entry.png to /output."""
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
OUTDIR = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
os.makedirs(OUTDIR, exist_ok=True)
shutil.copyfile(os.path.join(HERE, "entry.png"),
                os.path.join(OUTDIR, "entry.png"))
