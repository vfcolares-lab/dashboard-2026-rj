#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Geocodifica endereços usando OpenStreetMap Nominatim
Obtém coordenadas reais para cada local de votação
"""

import json
import re
import requests
import time
from collections import defaultdict

print("=" * 80)
print("GEOCODIFICANDO ENDEREÇOS DO RIO DE JANEIRO")
print("=" * 80)
print("Usando OpenStreetMap Nominatim (gratuito, 1 req/seg)")
print()

# Load current data
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    data = json.loads(match.group(1))

# Collect all unique addresses
endercos_unicos = {}  # {municipio|endereco: {local_nome, coords (if found)}}
total_endercos = 0

for municipio, mun_data in data['municipios'].items():
    for local in mun_data.get('locais_votacao', []):
        chave = f"{municipio}|{local['local_endereco']}"
        if chave not in endercos_unicos:
            endercos_unicos[chave] = {
                'municipio': municipio,
                'endereco': local['local_endereco'],
                'local_nome': local['local_nome']
            }
            total_endercos += 1

print(f"Total de endereços únicos a geocodificar: {total_endercos}\n")

# Nominatim API
NOMINATIM_URL = "https://nominatim.openstreetmap.org/search"
HEADERS = {'User-Agent': 'ElectoralDashboardRJ/1.0'}

geocodificados = 0
nao_encontrados = []

print("Geocodificando (pode levar alguns minutos)...\n")

for idx, (chave, info) in enumerate(endercos_unicos.items()):
    municipio = info['municipio']
    endereco = info['endereco']

    # Build search query
    query = f"{endereco}, {municipio}, Rio de Janeiro, Brasil"

    try:
        # Query Nominatim
        params = {
            'q': query,
            'format': 'json',
            'limit': 1,
            'timeout': 10
        }

        response = requests.get(NOMINATIM_URL, params=params, headers=HEADERS, timeout=15)

        if response.status_code == 200:
            results = response.json()

            if results:
                # Got a result
                lat = float(results[0]['lat'])
                lon = float(results[0]['lon'])
                info['latitude'] = round(lat, 5)
                info['longitude'] = round(lon, 5)
                geocodificados += 1

                if (idx + 1) % 500 == 0:
                    print(f"  ✓ {idx + 1}/{total_endercos} geocodificados...")
            else:
                # No results found
                nao_encontrados.append({
                    'municipio': municipio,
                    'endereco': endereco,
                    'motivo': 'Não encontrado no OSM'
                })
        else:
            nao_encontrados.append({
                'municipio': municipio,
                'endereco': endereco,
                'motivo': f'Erro HTTP {response.status_code}'
            })

    except Exception as e:
        nao_encontrados.append({
            'municipio': municipio,
            'endereco': endereco,
            'motivo': str(e)[:50]
        })

    # Rate limit: 1 request per second
    time.sleep(1.1)

print(f"\n✅ Geocodificados: {geocodificados}/{total_endercos}")
print(f"⚠️  Não encontrados: {len(nao_encontrados)}")

if nao_encontrados:
    print("\nExemplos de não encontrados:")
    for item in nao_encontrados[:5]:
        print(f"  {item['municipio']}: {item['endereco'][:40]}")
        print(f"    Motivo: {item['motivo']}\n")

# Update data with coordinates
print("\nAtualizando data-rj.js com coordenadas...\n")

updated_count = 0
for municipio, mun_data in data['municipios'].items():
    for local in mun_data.get('locais_votacao', []):
        chave = f"{municipio}|{local['local_endereco']}"
        if chave in endercos_unicos and 'latitude' in endercos_unicos[chave]:
            local['latitude'] = endercos_unicos[chave]['latitude']
            local['longitude'] = endercos_unicos[chave]['longitude']
            updated_count += 1

print(f"✅ {updated_count} locais atualizados com coordenadas reais\n")

# Save
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print("=" * 80)
print(f"✅ Geocodificação concluída!")
print(f"   Coordenadas reais adicionadas a {geocodificados} endereços")
print("=" * 80)

# Sample verification
sample = None
for mun_data in data['municipios'].values():
    for local in mun_data.get('locais_votacao', []):
        if 'latitude' in local and local['latitude'] != 0:
            sample = local
            break
    if sample:
        break

if sample:
    print(f"\n📍 Exemplo de local geocodificado:")
    print(f"   Nome: {sample['local_nome']}")
    print(f"   Endereço: {sample['local_endereco']}")
    print(f"   Coordenadas: ({sample['latitude']}, {sample['longitude']})")

