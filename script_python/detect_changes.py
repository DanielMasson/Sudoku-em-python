"""
Detecção de mudanças a partir de dois NDVIs (antes/depois).

Fluxo:
1. diferença = ndvi_antes - ndvi_depois  (positivo = perda de vegetação)
2. aplica um limiar (threshold) para criar uma máscara binária
3. remove ruído (pixels isolados) com uma abertura morfológica
4. identifica regiões conectadas (cada uma vira uma "ocorrência" candidata)

Nota: em produção, o passo 4 seria feito com rasterio.features.shapes +
shapely para gerar polígonos GeoJSON com coordenadas reais. Aqui,
como não há rasterio disponível no ambiente de teste, uso
skimage.measure.label/regionprops, que dá o mesmo tipo de resultado
(regiões e suas métricas), só que em coordenadas de pixel em vez de
lat/lon. A troca de um para o outro é direta.
"""

from dataclasses import dataclass

import numpy as np
from scipy import ndimage
from skimage import measure


@dataclass
class OcorrenciaDetectada:
    id: int
    area_pixels: int
    centroide_linha: float
    centroide_coluna: float
    bbox: tuple  # (min_linha, min_col, max_linha, max_col)
    queda_media_ndvi: float


def detectar_mudancas(
    ndvi_antes: np.ndarray,
    ndvi_depois: np.ndarray,
    limiar: float = 0.15,
    area_minima_pixels: int = 20,
):
    """
    Compara dois NDVIs e retorna:
    - mascara: array booleano com as áreas alteradas
    - ocorrencias: lista de OcorrenciaDetectada, uma por região conectada
    """
    diferenca = ndvi_antes - ndvi_depois  # positivo = perda de vegetação

    mascara_bruta = diferenca > limiar

    # Abertura morfológica: remove pixels isolados (ruído de sensor)
    mascara_limpa = ndimage.binary_opening(mascara_bruta, structure=np.ones((3, 3)))

    rotulos, n_regioes = ndimage.label(mascara_limpa)
    propriedades = measure.regionprops(rotulos, intensity_image=diferenca)

    ocorrencias = []
    for i, regiao in enumerate(propriedades, start=1):
        if regiao.area < area_minima_pixels:
            continue  # descarta regiões pequenas demais (provável ruído)

        min_linha, min_col, max_linha, max_col = regiao.bbox
        ocorrencias.append(
            OcorrenciaDetectada(
                id=i,
                area_pixels=int(regiao.area),
                centroide_linha=float(regiao.centroid[0]),
                centroide_coluna=float(regiao.centroid[1]),
                bbox=(min_linha, min_col, max_linha, max_col),
                queda_media_ndvi=float(regiao.intensity_mean),
            )
        )

    return mascara_limpa, ocorrencias


def pixel_para_coordenada(linha, coluna, origem_lat=-27.2423, origem_lon=-48.6356, resolucao_graus=0.0001):
    """
    Conversão simplificada de pixel -> lat/lon, só para a demo ter
    coordenadas plausíveis na "ordem de serviço". Em produção isso vem
    do georreferenciamento real da imagem (rasterio transform / GEE).
    """
    lat = origem_lat - (linha * resolucao_graus)
    lon = origem_lon + (coluna * resolucao_graus)
    return lat, lon
