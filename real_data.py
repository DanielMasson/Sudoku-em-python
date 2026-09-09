"""
Carrega bandas reais do Sentinel-2 (baixadas do Copernicus Browser)
para usar no mesmo pipeline que antes rodava com dados sintéticos.

Requer rasterio instalado (não disponível no sandbox de teste, mas
disponível no ambiente de vocês com internet):

    pip install rasterio

Uso:
    from real_data import carregar_banda, carregar_par_red_nir

    red, nir, transform, crs = carregar_par_red_nir(
        "dados/antes_B04.tif", "dados/antes_B08.tif"
    )
"""

import numpy as np
import rasterio


def carregar_banda(caminho_tif):
    """Lê um único arquivo GeoTIFF e retorna (array, transform, crs)."""
    with rasterio.open(caminho_tif) as src:
        banda = src.read(1).astype(np.float32)
        transform = src.transform
        crs = src.crs

    banda = _normalizar_banda(banda)
    return banda, transform, crs


def _normalizar_banda(banda):
    """
    Trata os dois formatos mais comuns de export do Sentinel Hub:
    - uint16 com reflectância x10000 -> divide por 10000
    - float32 já em reflectância (0-1), possivelmente com NaN nos
      pixels sem dado (nuvem/borda) -> substitui NaN por 0
    """
    n_nan = np.isnan(banda).sum()
    if n_nan > 0:
        print(f"Aviso: {n_nan} pixels sem dado (NaN) substituídos por 0.")
        banda = np.nan_to_num(banda, nan=0.0)

    if banda.max() > 1.5:
        banda = banda / 10000.0

    return banda


def carregar_multibanda(caminho_tif, indice_banda_red=1, indice_banda_nir=2):
    """
    Usar quando o Copernicus Browser baixou UM ÚNICO arquivo .tiff
    contendo várias bandas empilhadas (comum no modo "Analytical").

    indice_banda_red / indice_banda_nir: número da banda dentro do
    arquivo (1-indexado, na ordem em que você pediu as bandas no
    Browser). Rode inspecionar_tif.py no arquivo para confirmar qual
    índice corresponde a qual banda antes de usar isso.
    """
    with rasterio.open(caminho_tif) as src:
        red = src.read(indice_banda_red).astype(np.float32)
        nir = src.read(indice_banda_nir).astype(np.float32)
        transform = src.transform
        crs = src.crs

    red = _normalizar_banda(red)
    nir = _normalizar_banda(nir)

    return red, nir, transform, crs


def carregar_ndvi_direto(caminho_tif):
    """
    Usar quando o próprio Copernicus Browser já exportou o NDVI pronto
    (visualização "NDVI" em vez de bandas separadas B04/B08).

    Lida com os formatos de escala mais comuns:
    - float32 já em -1 a 1 -> usa direto
    - int16/uint8 escalado (ex: NDVI*100 ou NDVI*10000) -> normaliza
    """
    with rasterio.open(caminho_tif) as src:
        ndvi = src.read(1).astype(np.float32)
        transform = src.transform
        crs = src.crs

    n_nan = np.isnan(ndvi).sum()
    if n_nan > 0:
        ndvi = np.nan_to_num(ndvi, nan=0.0)

    maximo = ndvi.max()
    if maximo > 100:      # provavelmente escalado por 10000
        ndvi = ndvi / 10000.0
    elif maximo > 1.5:    # provavelmente escalado por 100 ou 255
        ndvi = ndvi / 100.0

    print(f"{caminho_tif}: NDVI min={ndvi.min():.3f} max={ndvi.max():.3f} média={ndvi.mean():.3f}")
    return ndvi, transform, crs


def carregar_par_red_nir(caminho_red, caminho_nir):
    """
    Lê as bandas B04 (red) e B08 (nir) de uma mesma cena.
    Retorna (red, nir, transform, crs) — transform e crs vêm do arquivo
    red e servem para georreferenciar as ocorrências detectadas depois.
    """
    red, transform, crs = carregar_banda(caminho_red)
    nir, _, _ = carregar_banda(caminho_nir)

    if red.shape != nir.shape:
        raise ValueError(
            f"RED e NIR têm tamanhos diferentes: {red.shape} vs {nir.shape}. "
            "Confira se as duas bandas foram baixadas com a mesma resolução/AOI."
        )

    return red, nir, transform, crs


def pixel_para_coordenada_real(linha, coluna, transform):
    """
    Substitui a função pixel_para_coordenada() inventada de detect_changes.py
    por uma conversão real, usando o transform (Affine) lido do GeoTIFF.
    """
    lon, lat = rasterio.transform.xy(transform, linha, coluna)
    return lat, lon