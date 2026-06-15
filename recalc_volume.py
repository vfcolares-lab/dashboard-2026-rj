#!/usr/bin/env python3
import csv
import json
from collections import defaultdict

print('📊 Recalculando volume eleitoral (apenas PRESIDENTE 2022)...\n')

# Carregar dados atuais
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    import re
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    data = json.loads(match.group(1))

# Ler dados presidenciais de BR
volume_por_endereco = defaultdict(lambda: {'lula': 0, 'bolsonaro': 0, 'seções': set()})
volume_por_municipio = defaultdict(lambda: {'lula': 0, 'bolsonaro': 0})

with open('/Users/vitorcolares/Downloads/votacao_secao_2022_BR/votacao_secao_2022_BR.csv', 'r', encoding='latin-1') as f:
    reader = csv.DictReader(f, delimiter=';')
    count = 0
    for row in reader:
        # Filtrar apenas RIO DE JANEIRO
        uf = row['SG_UF'].strip('"')
        if uf != 'RJ':
            continue

        # Filtrar apenas PRESIDENTE e PRIMEIRO TURNO
        if '"PRESIDENTE"' not in row['DS_CARGO'] and 'PRESIDENTE' not in row['DS_CARGO']:
            continue

        turno = row['NR_TURNO'].strip('"')
        if turno != '1':
            continue

        municipio = row['NM_MUNICIPIO'].strip('"')
        endereco = row['DS_LOCAL_VOTACAO_ENDERECO'].strip('"')
        secao = int(row['NR_SECAO'].strip('"'))
        votos = int(row['QT_VOTOS'].strip('"'))
        candidato = row['NM_VOTAVEL'].strip('"')

        # Consolidar por município + endereço
        chave = f"{municipio}|{endereco}"

        if 'LULA' in candidato.upper():
            volume_por_endereco[chave]['lula'] += votos
            volume_por_municipio[municipio]['lula'] += votos
        elif 'BOLSONARO' in candidato.upper():
            volume_por_endereco[chave]['bolsonaro'] += votos
            volume_por_municipio[municipio]['bolsonaro'] += votos

        volume_por_endereco[chave]['seções'].add(secao)
        count += 1

print(f'✅ Lidos {count} registros presidenciais\n')

# Atualizar data-rj.js com volumes corretos
for municipio, dados in data['municipios'].items():
    for local in dados['locais_votacao']:
        chave = f"{municipio}|{local['local_endereco']}"

        if chave in volume_por_endereco:
            lula_votos = volume_por_endereco[chave]['lula']
            bolsonaro_votos = volume_por_endereco[chave]['bolsonaro']

            # Atualizar volume
            local['volume_eleitoral'] = lula_votos
            local['lula_votos'] = lula_votos
            local['bolsonaro_votos'] = bolsonaro_votos

            # Recalcular Tamanho Aquário
            total_votos = lula_votos + bolsonaro_votos
            if total_votos > 0:
                local['tamanho_aquario_pct'] = (lula_votos / total_votos) * 100

            # Recalcular Índice de Exploração
            # Fórmula: % de Lindbergh em relação aos votos Lula nesse local
            lindbergh_local = local.get('lindbergh_votos', 0)
            local['indice_exploracao'] = (lindbergh_local / lula_votos * 100) if lula_votos > 0 else 0

# Atualizar agregados
total_lula_rj = sum(v['lula'] for v in volume_por_municipio.values())
total_bolsonaro_rj = sum(v['bolsonaro'] for v in volume_por_municipio.values())

data['metadata']['agregados_estaduais']['lula_votos'] = total_lula_rj
data['metadata']['agregados_estaduais']['bolsonaro_votos'] = total_bolsonaro_rj

print(f'📊 Volume Lula RJ: {total_lula_rj:,}')
print(f'📊 Volume Bolsonaro RJ: {total_bolsonaro_rj:,}\n')

# Salvar atualizado
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print('✅ data-rj.js recalculado com dados presidenciais corretos!')
