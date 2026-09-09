"""
Teste ponta a ponta do pipeline de detecção automática de mudanças
por imagem de satélite, usando dados sintéticos.

Rodar: python3 main.py
Saída: imprime as "ordens de serviço" detectadas e salva um PNG
       (resultado_deteccao.png) com o painel visual.
"""

import json

from synthetic_data import gerar_cena
from ndvi import calcular_ndvi
from detect_changes import detectar_mudancas, pixel_para_coordenada
from visualize import salvar_painel


def main():
    print("=== Gerando cenas sintéticas (antes / depois) ===")
    red_antes, nir_antes = gerar_cena(com_desmatamento=False)
    red_depois, nir_depois = gerar_cena(com_desmatamento=True)

    print("=== Calculando NDVI ===")
    ndvi_antes = calcular_ndvi(red_antes, nir_antes)
    ndvi_depois = calcular_ndvi(red_depois, nir_depois)
    print(f"NDVI médio antes:  {ndvi_antes.mean():.3f}")
    print(f"NDVI médio depois: {ndvi_depois.mean():.3f}")

    print("\n=== Detectando mudanças (limiar=0.15) ===")
    mascara, ocorrencias = detectar_mudancas(ndvi_antes, ndvi_depois, limiar=0.15)

    if not ocorrencias:
        print("Nenhuma ocorrência detectada. Tente reduzir o limiar.")
        return

    print(f"{len(ocorrencias)} ocorrência(s) detectada(s):\n")

    ordens_de_servico = []
    for oc in ocorrencias:
        lat, lon = pixel_para_coordenada(oc.centroide_linha, oc.centroide_coluna)
        ordem = {
            "id_ocorrencia": oc.id,
            "area_pixels": oc.area_pixels,
            "queda_media_ndvi": round(oc.queda_media_ndvi, 3),
            "centro_estimado": {"lat": round(lat, 6), "lon": round(lon, 6)},
            "bbox_pixel": oc.bbox,
            "status": "aguardando verificação em campo",
        }
        ordens_de_servico.append(ordem)
        print(json.dumps(ordem, ensure_ascii=False, indent=2))

    with open("ordens_de_servico.json", "w", encoding="utf-8") as f:
        json.dump(ordens_de_servico, f, ensure_ascii=False, indent=2)
    print("\nOrdens de serviço salvas em: ordens_de_servico.json")

    salvar_painel(ndvi_antes, ndvi_depois, mascara, ocorrencias, "resultado_deteccao.png")
    print("Painel visual salvo em: resultado_deteccao.png")


if __name__ == "__main__":
    main()
