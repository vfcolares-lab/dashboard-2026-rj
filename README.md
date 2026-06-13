# Dashboard Eleitoral - Rio de Janeiro 2026
## Análise Territorial de Lindbergh Farias Filho

### 📊 Dados
- **1º Turno 2022**
- Lula (PT): 3,847,143 votos
- Bolsonaro (PL): 4,831,246 votos  
- Lindbergh Farias Filho (PT): 59,062 votos (1.54%)

### 🎯 Cobertura
- **Municípios**: 92
- **Locais de Votação Únicos**: 4,659 (consolidados por endereço de 15.385 seções eleitorais)
- **Indicadores por Local**: 4 estratégicos

### 4️⃣ Indicadores Estratégicos

1. **🌊 Tamanho do Aquário** (10% - 85%)
   - % de votos Lula vs Bolsonaro em cada local
   - Mostra afinidade ideológica: altos = Lula, baixos = Bolsonaro

2. **📊 Volume Eleitoral** (absoluto)
   - Número total de votos Lula em cada local
   - Indica tamanho do mercado a ser explorado

3. **🎯 Índice de Exploração** (0.00x - 1.00x)
   - Taxa de penetração de Lindbergh por local
   - Comparado com média estadual (1.54%)
   - Mostra onde há maior margem de crescimento

4. **📈 Consistência Histórica** (4/10 - 8.5/10)
   - Estabilidade eleitoral do local
   - Baseado em dispersão do Aquário
   - Altos valores = mercado consolidado

### 📍 Coordenadas
- Distribuição aleatória dentro de 6km do centro de cada município
- Padrão seguido do dashboard Paraná (privacidade preservada)
- Visualização geográfica no mapa Leaflet.js

### 📱 Interface
- **3 Abas Principais**:
  1. Overview - Mapa e estatísticas gerais
  2. Indicadores - Tabela filtrada por município
  3. Preditivo - Análise e previsões

- **Funcionalidades**:
  - Dropdown de seleção de município
  - Tabela dinâmica com 7 colunas (Local | Endereço | 4 Indicadores | Lat/Lon)
  - Busca e filtro de resultados
  - Download CSV para Meta Ads targeting

### 🚀 Inicialização

```bash
cd /Users/vitorcolares/Desktop/dashboard-2026-rj
node server-local.js
```

Acesse: http://localhost:8000

### 📁 Estrutura
```
dashboard-2026-rj/
├── index.html          # Interface principal
├── data-rj.js          # Dados consolidados (4.659 locais + agregados)
├── coords_rj.json      # Coordenadas dos 92 municípios
├── secoes_2022_rj.json # Dados granulares das 15.385 seções
├── server-local.js     # Servidor Node.js
├── add_coordinates_rj.py    # Script para adicionar coords com offset
├── recalc_volume.py         # Script para recalcular volumes
└── README.md           # Este arquivo
```

### ✅ Validação
- ✓ Volumes consolidados = 3,847,143 (match estado)
- ✓ 4 indicadores presentes em todos os locais
- ✓ Coordenadas distribuídas (não mais duplicadas)
- ✓ Independente dos dashboards Paraná/Amazonas
- ✓ Pronto para análise territorial

---
**MERIDIAN Philosophy**: "Cada urna, um território"
