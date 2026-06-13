#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Adiciona coordenadas geográficas (latitude/longitude) a cada local de votação
Usa coordenadas do município + offset aleatório dentro do raio especificado
Mesmo padrão do dashboard Paraná
"""

import json
import random
import math
import re
from pathlib import Path

# Carregar coordenadas dos municípios RJ
with open('coords_rj.json', 'r', encoding='utf-8') as f:
    MUNICIPIOS_COORDS = json.load(f)

def add_random_offset(lat, lon, radius_km):
    """
    Adiciona um offset aleatório às coordenadas dentro do raio especificado.
    radius_km: raio em quilômetros
    Retorna: (nova_lat, nova_lon)
    """
    lat_rad = math.radians(lat)

    angle = random.uniform(0, 2 * math.pi)
    distance = random.uniform(0, radius_km)

    lat_offset = (distance * math.cos(angle)) / 111
    lon_offset = (distance * math.sin(angle)) / (111 * math.cos(lat_rad))

    new_lat = lat + lat_offset
    new_lon = lon + lon_offset

    return round(new_lat, 5), round(new_lon, 5)

print("=" * 80)
print("ADICIONANDO COORDENADAS AOS LOCAIS DE VOTAÇÃO DO RIO DE JANEIRO")
print("=" * 80)

# Load data from data-rj.js
with open('data-rj.js', 'r', encoding='utf-8') as f:
    conteudo = f.read()
    match = re.search(r'const DASHBOARD_DATA_RJ = ({.*});', conteudo, re.DOTALL)
    if not match:
        print("❌ Erro: não consegui extrair dados do data-rj.js")
        exit(1)
    data = json.loads(match.group(1))

total_locations = 0
locations_updated = 0

for municipio, municipio_data in data['municipios'].items():
    if municipio not in MUNICIPIOS_COORDS:
        print(f"⚠️  {municipio} - coordenadas não encontradas")
        continue

    base_lat, base_lon = MUNICIPIOS_COORDS[municipio]

    if 'locais_votacao' in municipio_data:
        for local in municipio_data['locais_votacao']:
            total_locations += 1
            # Reduzir raio em municípios perto de MG (lat > -21.3)
            raio_km = 3 if base_lat > -21.3 else 4  # Reduzido de 6km

            # Add coordinates with random offset
            lat, lon = add_random_offset(base_lat, base_lon, raio_km)
            local['latitude'] = lat
            local['longitude'] = lon
            locations_updated += 1

print(f"\n✅ Coordenadas adicionadas:")
print(f"  Total de locais: {total_locations}")
print(f"  Locais atualizados: {locations_updated}")

# Save updated data back to data-rj.js
with open('data-rj.js', 'w', encoding='utf-8') as f:
    f.write(f'const DASHBOARD_DATA_RJ = {json.dumps(data, ensure_ascii=False, indent=2)};')

print(f"\n💾 Arquivo salvo:")
print(f"  ✓ data-rj.js")

print("\n✅ Coordenadas prontas para o mapa!")

# Quick verification
sample_municipio = next(iter(data['municipios'].items()))
if sample_municipio[1].get('locais_votacao'):
    sample_local = sample_municipio[1]['locais_votacao'][0]
    print(f"\n📍 Exemplo de local com coordenadas:")
    print(f"  Município: {sample_municipio[0]}")
    print(f"  Local: {sample_local.get('local_nome', 'N/A')}")
    print(f"  Latitude: {sample_local['latitude']}")
    print(f"  Longitude: {sample_local['longitude']}")
