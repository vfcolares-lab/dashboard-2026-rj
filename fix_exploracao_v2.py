#!/usr/bin/env python3
"""
Recalcula Índice de Exploração com classificações percentil-based
Distribui os locais em 5 categorias baseadas na distribuição real
"""

import json
import re
import numpy as np

print("=" * 80)
print("RECALCULANDO ÍNDICE DE EXPLORAÇÃO COM PERCENTIS")
print("=" * 80 + "\n")

# Carregar dados
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    data = json.loads(match.group(1))

# Coletar todos os índices atuais
exploracoes = []
for mun_data in data['municipios'].values():
    for local in mun_data.get('locais_votacao', []):
        exploracoes.append(local['indice_exploracao'])

exploracoes_sorted = sorted(exploracoes)

# Calcular percentis
p10 = np.percentile(exploracoes_sorted, 10)
p30 = np.percentile(exploracoes_sorted, 30)
p70 = np.percentile(exploracoes_sorted, 70)
p90 = np.percentile(exploracoes_sorted, 90)

print(f"📊 DISTRIBUIÇÃO ATUAL:")
print(f"   P10 (bottom 10%): {p10:.4f}")
print(f"   P30 (bottom 30%): {p30:.4f}")
print(f"   P70 (bottom 70%): {p70:.4f}")
print(f"   P90 (bottom 90%): {p90:.4f}")
print(f"   Min: {min(exploracoes):.4f}")
print(f"   Max: {max(exploracoes):.4f}")

print(f"\n🎯 NOVOS LIMITES POR PERCENTIL:")
print(f"   ⚫ Não explorado: < {p10:.4f}")
print(f"   🔴 Pouco explorado: {p10:.4f} - {p30:.4f}")
print(f"   🟡 Moderado: {p30:.4f} - {p70:.4f}")
print(f"   🟠 Explorado: {p70:.4f} - {p90:.4f}")
print(f"   🔥 Hiperexplorado: > {p90:.4f}")

# Calcular nova classificação
classificacoes_novas = {
    'NAO_EXPLORADO': 0,
    'POUCO_EXPLORADO': 0,
    'MODERADO': 0,
    'EXPLORADO': 0,
    'HIPEREXPLORADO': 0,
}

count = 0
for mun_data in data['municipios'].values():
    for local in mun_data.get('locais_votacao', []):
        idx = local['indice_exploracao']

        # Determinar classificação
        if idx < p10:
            classificacao = 'NAO_EXPLORADO'
        elif idx < p30:
            classificacao = 'POUCO_EXPLORADO'
        elif idx < p70:
            classificacao = 'MODERADO'
        elif idx < p90:
            classificacao = 'EXPLORADO'
        else:
            classificacao = 'HIPEREXPLORADO'

        # Armazenar classificação (opcional, para usar depois)
        local['exploracao_categoria'] = classificacao
        classificacoes_novas[classificacao] += 1
        count += 1

print(f"\n✅ NOVA DISTRIBUIÇÃO (4,659 locais):")
for cat, c in classificacoes_novas.items():
    pct = 100 * c / count
    print(f"   {cat}: {c} ({pct:.1f}%)")

# Salvar
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print(f"\n✅ data-rj.js atualizado com classificações percentil-based!")
print(f"\n📝 Nota: As classificações agora refletem a distribuição real dos dados.")
print(f"   Mesmo que numericamente pareçam altos (0.9-1.0), a distribuição")
print(f"   percentil mostra quem realmente é explorado vs não-explorado.")
