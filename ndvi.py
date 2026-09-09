"""
Cálculo do NDVI (Normalized Difference Vegetation Index).

NDVI = (NIR - RED) / (NIR + RED)

Valores próximos de +1 indicam vegetação densa/saudável.
Valores próximos de 0 ou negativos indicam solo exposto, água ou
área construída/desmatada.
"""

import numpy as np


def calcular_ndvi(red: np.ndarray, nir: np.ndarray) -> np.ndarray:
    """Recebe as bandas RED e NIR (mesma forma) e retorna o NDVI."""
    red = red.astype(np.float32)
    nir = nir.astype(np.float32)

    denominador = nir + red
    # Evita divisão por zero em pixels sem sinal (ex: bordas de nuvem)
    denominador[denominador == 0] = 1e-6

    ndvi = (nir - red) / denominador
    return ndvi
