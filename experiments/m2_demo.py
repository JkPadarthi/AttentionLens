"""M2 gate: dual-view extraction for ResNet AND ViT on a real image.

Mirrors m1_demo.py but adds the ViT extractor so both architectures produce
LayerMaps in the same schema — the "apples-to-apples" claim becomes visible.
"""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from attentionlens.preprocess import load_image_tensor, tensor_to_image
from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.extractors.vit_extractor import VitExtractor


def show(maps, base, title, out_dir):
    import numpy as np
    for m in maps:
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        ax[0].imshow(base)
        ax[0].set_title(f"{m.layer_name} | {m.view}")
        ax[1].imshow(m.map, cmap="jet", alpha=0.7)
        ax[1].imshow(base, alpha=0.3)
        ax[1].axis("off")
        safe = f"{title}_{m.layer_name}_{m.view}".replace(".", "_").replace("/", "_")
        fig.savefig(f"{out_dir}/{safe}.png", bbox_inches="tight")
        plt.close(fig)


def main(img_path: str, out_dir: str = "experiments/out_m2"):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    x = load_image_tensor(img_path, device=device)
    base = tensor_to_image(x)
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)

    for name, ext in [("resnet", ResNetExtractor(device=device)),
                      ("vit", VitExtractor(device=device))]:
        insp = ext.inspect(x, image_id=pathlib.Path(img_path).stem)
        print(f"[{name}] pred={insp.pred_label} layers={len(insp.layers)}")
        show(insp.layers, base, name, out_dir)
    print(f"saved dual-view maps to {out_dir}/")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "experiments/sample.jpg",
         sys.argv[2] if len(sys.argv) > 2 else "experiments/out_m2")