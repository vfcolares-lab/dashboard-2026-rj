#!/usr/bin/env python3
import csv
import json
import re
from collections import defaultdict
import statistics

print('📊 Calculando Consistência Histórica REAL (2010-2022)...\n')

# Carregar data-rj.js
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    data = json.loads(match.group(1))

# Dicionário para armazenar histórico por município
# Usando candidatos PT: Dilma (2010, 2014), Haddad (2018), Lula (2022)
historico_por_municipio = defaultdict(lambda: {'anos': {}})

# Candidatos PT em cada eleição
candidatos_pt = {
    2010: ['DILMA VANA ROUSSEFF'],
    2014: ['DILMA VANA ROUSSEFF'],
    2018: ['FERNANDO HADDAD'],
    2022: ['LUIZ INÁCIO LULA DA SILVA', 'LULA'],
}

anos_eleicoes = {
    2010: '/Users/vitorcolares/Downloads/votacao_secao_2010_BR/votacao_secao_2010_BR.csv',
    2014: '/Users/vitorcolares/Downloads/votacao_secao_2014_BR/votacao_secao_2014_BR.csv',
    2018: '/Users/vitorcolares/Downloads/votacao_secao_2018_BR/votacao_secao_2018_BR.csv',
    2022: '/Users/vitorcolares/Downloads/votacao_secao_2022_BR/votacao_secao_2022_BR.csv',
}

print('Processando eleições (candidatos PT)...\n')

for ano, arquivo in anos_eleicoes.items():
    print(f'  {ano}...', end='', flush=True)

    pt_por_municipio = defaultdict(int)
    direita_por_municipio = defaultdict(int)

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

                # PT
                candidato_upper = candidato.upper()
                if any(cand in candidato_upper for cand in candidatos_pt[ano]):
                    pt_por_municipio[municipio] += votos
                # Direita (opositores principais)
                elif any(nome in candidato_upper for nome in ['SERRA', 'BOLSONARO', 'AÉCIO', 'MORO']):
                    direita_por_municipio[municipio] += votos

        # Calcular % PT por município
        for municipio in set(list(pt_por_municipio.keys()) + list(direita_por_municipio.keys())):
            pt = pt_por_municipio[municipio]
            direita = direita_por_municipio[municipio]
            total = pt + direita

            if total > 0:
                pct_pt = (pt / total) * 100
                historico_por_municipio[municipio]['anos'][ano] = pct_pt

    except FileNotFoundError:
        print(' (arquivo não encontrado)')
        continue

    print(' ✓')

print()

# Calcular Consistência Histórica para cada local
print('Calculando consistência para cada local...')

consistencia_count = 0
stats = []

for municipio, dados in data['municipios'].items():
    if municipio not in historico_por_municipio:
        continue

    anos_dict = historico_por_municipio[municipio]['anos']

    if len(anos_dict) >= 2:
        valores = list(anos_dict.values())

        # Calcular desvio padrão e coeficiente de variação
        media = statistics.mean(valores)
        desvio = statistics.stdev(valores) if len(valores) > 1 else 0

        # Coeficiente de variação (%)
        cv = (desvio / media * 100) if media > 0 else 0

        # Converter CV para escala 0-10
        # CV alta = pouca consistência, CV baixa = muita consistência
        # Usar uma escala razoável:
        # CV < 5% = 10 (muito estável)
        # CV 5-10% = 8
        # CV 10-15% = 6
        # CV 15-20% = 4
        # CV > 20% = 2 (instável)

        if cv < 5:
            consistencia = 10
        elif cv < 10:
            consistencia = 8
        elif cv < 15:
            consistencia = 6
        elif cv < 20:
            consistencia = 4
        else:
            consistencia = 2

        # Aplicar para todos os locais do município
        if 'locais_votacao' in dados:
            for local in dados['locais_votacao']:
                local['consistencia_historica'] = round(consistencia, 2)
                local['volatilidade_cv'] = round(cv, 2)
                local['historico_pt'] = {str(k): round(v, 2) for k, v in anos_dict.items()}
                consistencia_count += 1

        stats.append((municipio, consistencia, cv, valores))

print(f'✅ Consistência calculada para {consistencia_count} locais\n')

# Mostrar exemplos
print('Exemplos de Consistência Histórica (PT: Dilma→Haddad→Lula):')
print()
for municipio, consistencia, cv, valores in sorted(stats, key=lambda x: x[2])[:5]:
    print(f'{municipio}:')
    anos_sorted = sorted(historico_por_municipio[municipio]['anos'].items())
    for ano, pct in anos_sorted:
        print(f'  {ano}: {pct:.1f}%')
    print(f'  CV: {cv:.1f}% → Consistência: {consistencia:.0f}/10')
    print()

# Salvar
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print('✅ data-rj.js atualizado com Consistência Histórica REAL!')
