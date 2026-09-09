"""
Mesma lógica do main.py, mas usando arquivos GeoTIFF reais baixados
do Copernicus Browser, em vez de dados sintéticos.

Rodar (depois de baixar os arquivos e ajustar os caminhos abaixo):
    pip install rasterio
    python3 main_dados_reais.py
"""

import json

from ndvi import calcular_ndvi
from detect_changes import detectar_mudancas
from real_data import carregar_par_red_nir, pixel_para_coordenada_real
from visualize import salvar_painel

# --- Ajuste estes caminhos para os arquivos que vocês baixaram ---
CAMINHO_ANTES_RED = "dados/antes_B04.tiff"
CAMINHO_ANTES_NIR = "dados/antes_B08.tiff"
CAMINHO_DEPOIS_RED = "dados/depois_B04.tiff"
CAMINHO_DEPOIS_NIR = "dados/depois_B08.tiff"


def main():
    print("=== Carregando imagens reais do Sentinel-2 ===")
    red_antes, nir_antes, transform, crs = carregar_par_red_nir(CAMINHO_ANTES_RED, CAMINHO_ANTES_NIR)
    red_depois, nir_depois, _, _ = carregar_par_red_nir(CAMINHO_DEPOIS_RED, CAMINHO_DEPOIS_NIR)
    print(f"CRS da imagem: {crs}")
    print(f"Dimensões: {red_antes.shape}")

    print("\n=== Calculando NDVI ===")
    ndvi_antes = calcular_ndvi(red_antes, nir_antes)
    ndvi_depois = calcular_ndvi(red_depois, nir_depois)
    print(f"NDVI médio antes:  {ndvi_antes.mean():.3f}")
    print(f"NDVI médio depois: {ndvi_depois.mean():.3f}")

    print("\n=== Detectando mudanças ===")
    # Comecem com limiar=0.15 e ajustem observando o resultado --
    # imagem real tem mais ruído (nuvem residual, sombra, variação sazonal)
    # do que a sintética, então pode precisar subir o limiar ou o
    # area_minima_pixels para não pegar falso-positivo.
    mascara, ocorrencias = detectar_mudancas(ndvi_antes, ndvi_depois, limiar=0.15, area_minima_pixels=20)

    if not ocorrencias:
        print("Nenhuma ocorrência detectada. Tente reduzir o limiar.")
        return

    print(f"{len(ocorrencias)} ocorrência(s) detectada(s):\n")

    ordens_de_servico = []
    for oc in ocorrencias:
        lat, lon = pixel_para_coordenada_real(oc.centroide_linha, oc.centroide_coluna, transform)
        ordem = {
            "id_ocorrencia": oc.id,
            "area_pixels": oc.area_pixels,
            "area_m2_aprox": oc.area_pixels * 100,  # Sentinel-2 = 10m x 10m por pixel
            "queda_media_ndvi": round(oc.queda_media_ndvi, 3),
            "centro_estimado": {"lat": round(lat, 6), "lon": round(lon, 6)},
            "status": "aguardando verificação em campo",
        }
        ordens_de_servico.append(ordem)
        print(json.dumps(ordem, ensure_ascii=False, indent=2))

    with open("ordens_de_servico_real.json", "w", encoding="utf-8") as f:
        json.dump(ordens_de_servico, f, ensure_ascii=False, indent=2)
    print("\nOrdens de serviço salvas em: ordens_de_servico_real.json")

    salvar_painel(ndvi_antes, ndvi_depois, mascara, ocorrencias, "resultado_deteccao_real.png")
    print("Painel visual salvo em: resultado_deteccao_real.png")


if __name__ == "__main__":
    main()