# experiments/fetch_objectnet.py
"""Download the gated timm/objectnet-in1k dataset (113 ImageNet-overlapping classes).

Requires an authenticated HF session (token saved at ~/.cache/huggingface/token).
Run from the repo root on the GPU box. Downloads the parquet shards and places them
under data/objectnet-in1k/ so the real M8 experiment can load them with `datasets`.
"""
from __future__ import annotations

import argparse
import logging
from pathlib import Path

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(message)s")
log = logging.getLogger("fetch_objectnet")

REPO = "timm/objectnet-in1k"


def main():
    from huggingface_hub import snapshot_download

    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data/objectnet-in1k")
    ap.add_argument("--repo", default=REPO)
    args = ap.parse_args()

    out = Path(args.out)
    out.mkdir(parents=True, exist_ok=True)

    log.info("snapshot_download %s -> %s (this is ~17 GB; streaming)", args.repo, out)
    # token picked up from the saved login / HF_TOKEN env automatically.
    local = snapshot_download(repo_id=args.repo, repo_type="dataset",
                              local_dir=str(out), local_dir_use_symlinks=False)
    log.info("done: %s", local)
    # list what we got
    files = sorted(out.rglob("*"))
    n_parquet = sum(1 for p in files if p.suffix == ".parquet")
    log.info("files=%d parquet_shards=%d", len(files), n_parquet)


if __name__ == "__main__":
    main()