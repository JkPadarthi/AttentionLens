# experiments/m1_demo.py
"""M1 gate: run ResNet-50 on a real image, save dual-view maps for all blocks."""
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parents[1]))

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import torch

from attentionlens.extractors.resnet import ResNetExtractor
from attentionlens.preprocess import load_image_tensor, tensor_to_image


def main(img_path: str, out_dir: str = "experiments/out"):
    device = torch.device("cpu")
    x = load_image_tensor(img_path, device=device)
    ext = ResNetExtractor(device=device)
    insp = ext.inspect(x, image_id=pathlib.Path(img_path).stem)
    print(f"pred: {insp.pred_label} | true: {insp.true_label or 'n/a'} | layers: {len(insp.layers)}")

    base = tensor_to_image(x)
    pathlib.Path(out_dir).mkdir(parents=True, exist_ok=True)
    for m in insp.layers:
        fig, ax = plt.subplots(1, 2, figsize=(8, 4))
        ax[0].imshow(base)
        ax[0].set_title(f"{m.layer_name} | {m.view}")
        ax[0].axis("off")
        ax[1].imshow(base)
        ax[1].imshow(m.map, cmap="jet", alpha=0.7)
        ax[1].axis("off")
        fig.savefig(f"{out_dir}/{m.layer_name}_{m.view}.png", bbox_inches="tight")
        plt.close(fig)
    print(f"saved maps to {out_dir}/")


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "experiments/sample.jpg")
