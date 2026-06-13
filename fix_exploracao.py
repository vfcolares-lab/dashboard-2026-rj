#!/usr/bin/env python3
"""
Corrige o Índice de Exploração usando a taxa consolidada real (1.47%)
em vez de taxa que inclui votos não-consolidados (1.54%)
"""

import json
import re

print("=" * 80)
print("CORRIGINDO ÍNDICE DE EXPLORAÇÃO")
print("=" * 80 + "\n")

# Carregar dados
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    data = json.loads(match.group(1))

# Calcular totais REAIS consolidados
total_lindbergh = 0
total_lula = 0

for mun_data in data['municipios'].values():
    for local in mun_data.get('locais_votacao', []):
        total_lindbergh += local['lindbergh_votos']
        total_lula += local['lula_votos']

# Taxa estadual real
taxa_estadual_real = total_lindbergh / total_lula if total_lula > 0 else 0

print(f"📊 DADOS CONSOLIDADOS (4,659 locais):")
print(f"   Total Lindbergh: {total_lindbergh:,}")
print(f"   Total Lula: {total_lula:,}")
print(f"   Taxa Estadual: {taxa_estadual_real:.4f} ({taxa_estadual_real*100:.2f}%)")

# Atualizar metadata
data['metadata']['agregados_estaduais']['lindbergh_votos'] = total_lindbergh
data['metadata']['agregados_estaduais']['lula_votos'] = total_lula

print(f"\n🔄 RECALCULANDO ÍNDICE DE EXPLORAÇÃO...")

# Recalcular Índice de Exploração para cada local
count = 0
for mun_data in data['municipios'].values():
    for local in mun_data.get('locais_votacao', []):
        if local['lula_votos'] > 0:
            taxa_local = local['lindbergh_votos'] / local['lula_votos']
            novo_indice = taxa_local / taxa_estadual_real if taxa_estadual_real > 0 else 0
            local['indice_exploracao'] = novo_indice
            count += 1

print(f"   ✅ {count} locais atualizados")

# Salvar
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print(f"\n✅ data-rj.js atualizado com Índice de Exploração correto!")

# Verificar distribuição
exploracoes = []
for mun_data in data['municipios'].values():
    for local in mun_data.get('locais_votacao', []):
        exploracoes.append(local['indice_exploracao'])

exploracoes.sort()
print(f"\n📊 NOVA DISTRIBUIÇÃO:")
print(f"   Mín: {min(exploracoes):.3f}")
print(f"   Max: {max(exploracoes):.3f}")
print(f"   Média: {sum(exploracoes)/len(exploracoes):.3f}")
print(f"   Mediana: {exploracoes[len(exploracoes)//2]:.3f}")

ranges = {
    ">0.5x (Hiperexplorado)": sum(1 for e in exploracoes if e > 0.5),
    "0.3-0.5x (Explorado)": sum(1 for e in exploracoes if 0.3 <= e <= 0.5),
    "0.1-0.3x (Pouco explorado)": sum(1 for e in exploracoes if 0.1 <= e < 0.3),
    "<0.1x (Não explorado)": sum(1 for e in exploracoes if e < 0.1),
}

print(f"\n   Distribuição:")
for faixa, count in ranges.items():
    print(f"     {faixa}: {count} ({100*count/len(exploracoes):.1f}%)")
