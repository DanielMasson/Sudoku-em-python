"""
Caminho mais rápido: usa os arquivos NDVI que o próprio Copernicus
Browser já calculou (visualização "NDVI"), pulando o cálculo manual
via bandas B04/B08.

Ajuste os nomes de arquivo abaixo para os que você baixou.

Rodar:
    pip install rasterio
    python3 main_ndvi_direto.py
"""

import json

from detect_changes import detectar_mudancas, pixel_para_coordenada
from real_data import carregar_ndvi_direto, pixel_para_coordenada_real
from visualize import salvar_painel

# --- Ajuste para os nomes reais dos arquivos NDVI baixados ---
CAMINHO_NDVI_ANTES = "dados/2026-09-03-00_00_2026-09-03-23_59_Sentinel-2_L2A_NDVI.tiff"
CAMINHO_NDVI_DEPOIS = "dados/2026-09-08-00_00_2026-09-08-23_59_Sentinel-2_L2A_NDVI.tiff"


def main():
    print("=== Carregando NDVI já calculado pelo Copernicus Browser ===")
    ndvi_antes, transform, crs = carregar_ndvi_direto(CAMINHO_NDVI_ANTES)
    ndvi_depois, _, _ = carregar_ndvi_direto(CAMINHO_NDVI_DEPOIS)

    if ndvi_antes.shape != ndvi_depois.shape:
        raise ValueError(
            f"As duas imagens têm tamanhos diferentes: {ndvi_antes.shape} vs {ndvi_depois.shape}. "
            "Confira se foram baixadas com a mesma área/resolução no Browser."
        )

    print("\n=== Detectando mudanças ===")
    # Datas de 03/09 a 08/09 são só 5 dias -- mudança real de vegetação
    # nesse intervalo tende a ser pequena, então pode precisar de um
    # limiar bem mais baixo do que o usado nos dados sintéticos.
    mascara, ocorrencias = detectar_mudancas(ndvi_antes, ndvi_depois, limiar=0.05, area_minima_pixels=10)

    if not ocorrencias:
        print("Nenhuma ocorrência detectada com esse limiar. Tente reduzir mais (ex: 0.02).")
        return

    print(f"{len(ocorrencias)} ocorrência(s) detectada(s):\n")

    ordens_de_servico = []
    for oc in ocorrencias:
        lat, lon = pixel_para_coordenada_real(oc.centroide_linha, oc.centroide_coluna, transform)
        ordem = {
            "id_ocorrencia": oc.id,
            "area_pixels": oc.area_pixels,
            "area_m2_aprox": oc.area_pixels * 100,
            "queda_media_ndvi": round(oc.queda_media_ndvi, 3),
            "centro_estimado": {"lat": round(lat, 6), "lon": round(lon, 6)},
            "status": "aguardando verificação em campo",
        }
        ordens_de_servico.append(ordem)
        print(json.dumps(ordem, ensure_ascii=False, indent=2))

    with open("ordens_de_servico_ndvi_direto.json", "w", encoding="utf-8") as f:
        json.dump(ordens_de_servico, f, ensure_ascii=False, indent=2)
    print("\nOrdens de serviço salvas em: ordens_de_servico_ndvi_direto.json")

    salvar_painel(ndvi_antes, ndvi_depois, mascara, ocorrencias, "resultado_deteccao_ndvi_direto.png")
    print("Painel visual salvo em: resultado_deteccao_ndvi_direto.png")


if __name__ == "__main__":
    main()
