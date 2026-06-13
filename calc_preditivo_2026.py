#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Calcula Índice Preditivo 2026 para Lindbergh baseado em 4 dimensões
"""

import json
import re

print("=" * 80)
print("CALCULANDO ÍNDICE PREDITIVO 2026 — LINDBERGH FARIAS")
print("=" * 80 + "\n")

# Load data
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    data = json.loads(match.group(1))

municipios = []

for municipio_nome, municipio_data in data['municipios'].items():
    locais = municipio_data.get('locais_votacao', [])

    if not locais:
        continue

    # Agregar dados do município
    total_volume = sum(l['volume_eleitoral'] for l in locais)
    avg_aquario = sum(l['tamanho_aquario_pct'] for l in locais) / len(locais)
    avg_exploracao = sum(l['indice_exploracao'] for l in locais) / len(locais)
    avg_consistencia = sum(l['consistencia_historica'] for l in locais) / len(locais)

    # Normalizar volume (escala 0-10, onde 10 = top 25%)
    # Volume máximo é ~13k votos
    volume_score = min((total_volume / 5000), 10)

    # Aquário já está em % (0-100), normalizar para 0-10
    aquario_score = avg_aquario / 10

    # Oportunidade de exploração (quanto menor o índice, maior a oportunidade)
    # Se índice = 1.0, oportunidade = 0
    # Se índice = 0.5, oportunidade = 5
    oportunidade_score = max(0, (1.0 - avg_exploracao) * 10)

    # Consistência já está em 0-10
    consistencia_score = avg_consistencia

    # Score final (média ponderada)
    # 40% volume, 30% aquário, 20% oportunidade, 10% consistência
    score = (volume_score * 0.4 + aquario_score * 0.3 + oportunidade_score * 0.2 + consistencia_score * 0.1)

    # Classificar
    if score >= 7.5:
        classificacao = "BASTIÃO LINDBERGH"
        emoji = "🟢"
    elif score >= 6.5:
        classificacao = "FORTE PRÓ-LINDBERGH"
        emoji = "🟡"
    elif score >= 5.0:
        classificacao = "COMPETITIVO"
        emoji = "🟠"
    elif score >= 3.5:
        classificacao = "DESAFIO"
        emoji = "🔴"
    else:
        classificacao = "DIFÍCIL"
        emoji = "⚫"

    municipios.append({
        'nome': municipio_nome,
        'volume': total_volume,
        'aquario': avg_aquario,
        'exploracao': avg_exploracao,
        'consistencia': avg_consistencia,
        'score': score,
        'classificacao': classificacao,
        'emoji': emoji,
        'volume_score': volume_score,
        'aquario_score': aquario_score,
        'oportunidade_score': oportunidade_score,
        'consistencia_score': consistencia_score
    })

# Ordenar por score
municipios.sort(key=lambda x: x['score'], reverse=True)

# Adicionar ao data-rj.js
data['preditivo_2026'] = {
    'municipios': municipios,
    'timestamp': '2026-06-13',
    'metodologia': 'Híbrida: 40% Volume + 30% Aquário + 20% Oportunidade + 10% Consistência'
}

# Salvar
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

# Mostrar resultado
print("📊 RESULTADO DA PREDITIVA 2026:\n")

counts = {}
for mun in municipios:
    cls = mun['classificacao']
    counts[cls] = counts.get(cls, 0) + 1

for cls in ["BASTIÃO LINDBERGH", "FORTE PRÓ-LINDBERGH", "COMPETITIVO", "DESAFIO", "DIFÍCIL"]:
    if cls in counts:
        print(f"{counts[cls]:2d}x {cls}")

print("\n🏆 Top 10 Municípios para 2026:\n")
for i, mun in enumerate(municipios[:10], 1):
    print(f"{i:2d}. {mun['emoji']} {mun['nome']:30s} Score: {mun['score']:.2f} | Vol: {mun['volume']:,} | Aquário: {mun['aquario']:.1f}% | Exp: {mun['exploracao']:.2f}x")

print("\n✅ data-rj.js atualizado com preditivo 2026!")
