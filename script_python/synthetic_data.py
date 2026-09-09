"""
Gera dados sintéticos de teste: duas "imagens" (antes/depois), cada uma
com uma banda vermelha (RED) e uma banda infravermelho-próximo (NIR),
simulando o que viria de um recorte Sentinel-2 real.

Isso serve só para validar a LÓGICA do pipeline sem depender de
internet/credenciais do Google Earth Engine. Quando for usar dados
reais, troque só esta função por uma que baixa/recorta as bandas
B4 (red) e B8 (nir) do Sentinel-2 via earthengine-api ou rasterio.
"""

import numpy as np

RNG_SEED = 42


def gerar_cena(tamanho=200, com_desmatamento=False, semente=RNG_SEED):
    """
    Gera uma cena sintética com vegetação saudável em toda a área.

    Se com_desmatamento=True, insere uma região irregular (polígono
    aproximado por um blob) onde a vegetação foi removida — simulando
    o "depois" de uma ocorrência real.

    Retorna: (red, nir) como arrays numpy float32, shape (tamanho, tamanho)
    """
    rng = np.random.default_rng(semente)

    # Vegetação saudável: NIR alto, RED baixo (típico de vegetação viva)
    red = rng.normal(loc=0.08, scale=0.01, size=(tamanho, tamanho)).astype(np.float32)
    nir = rng.normal(loc=0.45, scale=0.03, size=(tamanho, tamanho)).astype(np.float32)

    if com_desmatamento:
        # Cria uma área irregular "desmatada" combinando dois blobs
        # circulares deslocados, pra não ficar um quadrado perfeito
        yy, xx = np.mgrid[0:tamanho, 0:tamanho]

        blob1 = (xx - 130) ** 2 / 35**2 + (yy - 70) ** 2 / 25**2 <= 1
        blob2 = (xx - 150) ** 2 / 20**2 + (yy - 95) ** 2 / 20**2 <= 1
        area_desmatada = blob1 | blob2

        # Solo exposto / vegetação removida: RED sobe, NIR cai
        red[area_desmatada] = rng.normal(0.22, 0.02, area_desmatada.sum())
        nir[area_desmatada] = rng.normal(0.20, 0.02, area_desmatada.sum())

    # Garante que os valores fiquem em faixa plausível de reflectância (0-1)
    red = np.clip(red, 0, 1)
    nir = np.clip(nir, 0, 1)

    return red, nir


if __name__ == "__main__":
    red_antes, nir_antes = gerar_cena(com_desmatamento=False)
    red_depois, nir_depois = gerar_cena(com_desmatamento=True)
    print("Cena 'antes':  red média=%.3f  nir média=%.3f" % (red_antes.mean(), nir_antes.mean()))
    print("Cena 'depois': red média=%.3f  nir média=%.3f" % (red_depois.mean(), nir_depois.mean()))
