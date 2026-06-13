#!/usr/bin/env python3
import csv
import json
import re
from collections import defaultdict
import statistics

print('📊 Calculando Consistência Histórica (2018-2022)...\n')

# Carregar data-rj.js
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    data = json.loads(match.group(1))

# Dicionário para armazenar histórico por município
historico_por_municipio = defaultdict(lambda: {'anos': {}})

# Processar cada ano (apenas 2018 e 2022 que têm Lula)
anos_eleicoes = {
    2018: '/Users/vitorcolares/Downloads/votacao_secao_2018_BR/votacao_secao_2018_BR.csv',
    2022: '/Users/vitorcolares/Downloads/votacao_secao_2022_BR/votacao_secao_2022_BR.csv',
}

print('Processando eleições...\n')

for ano, arquivo in anos_eleicoes.items():
    print(f'  {ano}...', end='', flush=True)

    lula_por_municipio = defaultdict(int)
    bolsonaro_por_municipio = defaultdict(int)

    try:
        with open(arquivo, 'r', encoding='latin-1') as f:
            reader = csv.DictReader(f, delimiter=';')

            for row in reader:
                # Filtrar apenas RJ e PRESIDENTE
                uf = row.get('SG_UF', '').strip('"')
                if uf != 'RJ':
                    continue

                cargo = row.get('DS_CARGO', '').strip('"')
                if 'PRESIDENTE' not in cargo:
                    continue

                # Filtrar apenas 1º turno
                turno = row.get('NR_TURNO', '').strip('"')
                if turno != '1':
                    continue

                municipio = row.get('NM_MUNICIPIO', '').strip('"')
                candidato = row.get('NM_VOTAVEL', '').strip('"')
                votos = int(row.get('QT_VOTOS', '0').strip('"'))

                if 'LULA' in candidato.upper():
                    lula_por_municipio[municipio] += votos
                elif 'BOLSONARO' in candidato.upper():
                    bolsonaro_por_municipio[municipio] += votos

        # Calcular % Lula por município
        for municipio in set(list(lula_por_municipio.keys()) + list(bolsonaro_por_municipio.keys())):
            lula = lula_por_municipio[municipio]
            bolsonaro = bolsonaro_por_municipio[municipio]
            total = lula + bolsonaro

            if total > 0:
                pct_lula = (lula / total) * 100
                historico_por_municipio[municipio]['anos'][ano] = pct_lula

    except FileNotFoundError:
        print(' (arquivo não encontrado)')
        continue

    print(' ✓')

print()

# Calcular Consistência Histórica para cada local
print('Calculando consistência para cada local...')

consistencia_count = 0
for municipio, dados in data['municipios'].items():
    if municipio not in historico_por_municipio:
        continue

    anos_dict = historico_por_municipio[municipio]['anos']

    if len(anos_dict) >= 2:
        valores = list(anos_dict.values())

        # Com apenas 2 pontos, calcular a variação
        variacao = abs(valores[1] - valores[0])  # Diferença entre 2022 e 2018

        # Consistência: quanto menor a variação, maior a consistência
        # Escala 0-10 (0 = muito instável [>20pp variação], 10 = muito estável [<1pp variação])
        if variacao > 20:
            consistencia = 0  # Muito instável
        elif variacao > 15:
            consistencia = 2
        elif variacao > 10:
            consistencia = 4
        elif variacao > 5:
            consistencia = 6
        elif variacao > 2:
            consistencia = 8
        else:
            consistencia = 10  # Muito estável

        # Aplicar para todos os locais do município
        if 'locais_votacao' in dados:
            for local in dados['locais_votacao']:
                local['consistencia_historica'] = round(consistencia, 2)
                local['variacao_lula_pp'] = round(variacao, 2)
                local['historico_lula'] = {str(k): round(v, 2) for k, v in anos_dict.items()}
                consistencia_count += 1

print(f'✅ Consistência calculada para {consistencia_count} locais\n')

# Mostrar exemplos
print('Exemplos de Consistência Histórica (2018-2022):')
for municipio in ['RIO DE JANEIRO', 'NITERÓI', 'DUQUE DE CAXIAS']:
    if municipio in historico_por_municipio:
        anos = historico_por_municipio[municipio]['anos']
        variacao = abs(anos.get(2022, 0) - anos.get(2018, 0))
        print(f'\n{municipio}:')
        print(f'  2018: {anos.get(2018, 0):.1f}%')
        print(f'  2022: {anos.get(2022, 0):.1f}%')
        print(f'  Variação: {variacao:.1f}pp')
        if variacao < 2:
            print(f'  Consistência: 10/10 (Muito Estável)')
        elif variacao < 5:
            print(f'  Consistência: 8/10 (Estável)')
        elif variacao < 10:
            print(f'  Consistência: 6/10 (Moderado)')
        else:
            print(f'  Consistência: 4/10 (Instável)')

# Salvar
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print('\n✅ data-rj.js atualizado com Consistência Histórica!')
