#!/usr/bin/env python3
import json
import re

# Carregar coords dos municípios
with open('coords_rj.json', 'r', encoding='utf-8') as f:
    coords_municipios = json.load(f)

# Carregar data-rj.js
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()

# Extrair o objeto JSON
match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
if not match:
    print("❌ Erro: não consegui extrair dados do data-rj.js")
    exit(1)

data = json.loads(match.group(1))

# Adicionar coordenadas a cada local de votação
total_atualizados = 0
for municipio, dados in data['municipios'].items():
    if municipio not in coords_municipios:
        print(f"⚠️  Município {municipio} não encontrado em coords_rj.json")
        continue

    lat, lon = coords_municipios[municipio]

    if 'locais_votacao' in dados:
        for local in dados['locais_votacao']:
            local['latitude'] = lat
            local['longitude'] = lon
            total_atualizados += 1

print(f"✅ Coordenadas adicionadas a {total_atualizados} locais de votação")

# Salvar atualizado
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print("✅ data-rj.js atualizado com sucesso!")
