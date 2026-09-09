"""Gera um painel visual (PNG) para inspecionar o resultado do pipeline."""

import matplotlib.pyplot as plt
import numpy as np


def salvar_painel(ndvi_antes, ndvi_depois, mascara, ocorrencias, caminho_saida):
    fig, eixos = plt.subplots(1, 3, figsize=(15, 5))

    im0 = eixos[0].imshow(ndvi_antes, cmap="RdYlGn", vmin=-1, vmax=1)
    eixos[0].set_title("NDVI - antes")
    plt.colorbar(im0, ax=eixos[0], fraction=0.046)

    im1 = eixos[1].imshow(ndvi_depois, cmap="RdYlGn", vmin=-1, vmax=1)
    eixos[1].set_title("NDVI - depois")
    plt.colorbar(im1, ax=eixos[1], fraction=0.046)

    eixos[2].imshow(ndvi_depois, cmap="gray", vmin=-1, vmax=1)
    overlay = np.zeros((*mascara.shape, 4))
    overlay[mascara] = [1, 0, 0, 0.6]  # vermelho semi-transparente
    eixos[2].imshow(overlay)
    eixos[2].set_title(f"Áreas detectadas ({len(ocorrencias)} ocorrência(s))")

    for ax in eixos:
        ax.axis("off")

    plt.tight_layout()
    plt.savefig(caminho_saida, dpi=120)
    plt.close(fig)
