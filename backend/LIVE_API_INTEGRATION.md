# Integración con API de Football en Vivo

## Descripción General

Este documento explica cómo integrar los bots con la API en vivo de football para obtener partidos reales y actualizados.

## Configuración de la API

### 1. Obtener API Key
1. Visita [https://apifootball.com/](https://apifootball.com/)
2. Regístrate y obtén tu API key
3. Configura la variable de entorno:
```bash
export FOOTBALL_API_KEY="tu_clave_aqui"
```

### 2. Instalar Dependencias
```bash
pip install requests
```

### 3. Endpoint de la API
```
GET https://apiv2.apifootball.com/?action=get_events
    &APIkey=TU_API_KEY
    &league_id=ID_DE_LIGA
    &from=2025-07-22
    &to=2025-09-01
```

## IDs de Ligas Principales

| Liga | ID | Descripción |
|------|----|-----------| 
| Champions League | 3 | UEFA Champions League |
| Europa League | 4 | UEFA Europa League |
| Premier League | 152 | Liga Inglesa |
| Bundesliga | 175 | Liga Alemana |
| Serie A | 207 | Liga Italiana |
| La Liga | 302 | Liga Española |
| Ligue 1 | 168 | Liga Francesa |
| Conference League | 683 | UEFA Conference League |

## Uso del Script

### Obtener Todos los Partidos
```bash
python3 fetch_live_matches.py
```

### Solo Champions League
```bash
python3 fetch_live_matches.py --champions
```

### Integración Automática
Una vez configurado, el sistema cargará automáticamente los partidos en vivo:

```python
from match_data_loader import get_matches_for_bots

# Los bots usarán automáticamente datos en vivo si están disponibles
matches = get_matches_for_bots(competitions=None, with_referees=True)
```

## Estructura de Datos

### Formato de la API
```json
{
  "match_id": "12345",
  "match_date": "2025-07-22",
  "match_time": "20:00",
  "match_hometeam_name": "Real Madrid",
  "match_awayteam_name": "Barcelona",
  "match_hometeam_score": null,
  "match_awayteam_score": null,
  "match_status": "scheduled",
  "match_hometeam_odds": "2.10",
  "match_drawteam_odds": "3.40",
  "match_awayteam_odds": "3.20"
}
```

### Formato para Bots
```json
{
  "id": "12345",
  "home_team": "Real Madrid",
  "away_team": "Barcelona",
  "home_score": null,
  "away_score": null,
  "status": "scheduled",
  "time": "2025-07-22 20:00",
  "competition": "Champions League",
  "competition_type": "champions_league",
  "season": "2024/2025",
  "source": "live_api",
  "is_real": true,
  "match_time": "2025-07-22 20:00",
  "referee": "Björn Kuipers",
  "odds": {
    "home_win": 2.10,
    "draw": 3.40,
    "away_win": 3.20
  }
}
```

## Flujo de Trabajo

### 1. Obtención de Datos
```bash
# Ejecutar diariamente para obtener partidos actualizados
python3 fetch_live_matches.py
```

### 2. Procesamiento Automático
El sistema detecta automáticamente los nuevos archivos:
- `live_matches_YYYYMMDD.json`
- `champions_league_matches_YYYYMMDD.json`

### 3. Integración con Bots
```python
# Los bots cargan automáticamente todos los datos disponibles
from cards_bot import CardsBot
from corners_bot import CornersBot

cards_bot = CardsBot()
corners_bot = CornersBot()

# Obtener partidos en vivo
from match_data_loader import get_matches_for_bots
live_matches = get_matches_for_bots()

# Generar picks
cards_picks = cards_bot.get_picks_for_matches(live_matches)
corners_picks = corners_bot.get_picks_for_matches(live_matches)
```

## Ejemplo de Implementación

### Script Diario Automatizado
```bash
#!/bin/bash
# daily_update.sh

echo "🔄 Actualizando partidos..."
export FOOTBALL_API_KEY="tu_clave_aqui"
python3 fetch_live_matches.py

echo "🤖 Generando picks..."
python3 -c "
from match_data_loader import get_matches_for_bots
from cards_bot import CardsBot
from corners_bot import CornersBot

matches = get_matches_for_bots()
print(f'Partidos cargados: {len(matches)}')

cards_bot = CardsBot()
corners_bot = CornersBot()

cards_picks = cards_bot.get_picks_for_matches(matches)
corners_picks = corners_bot.get_picks_for_matches(matches)

print(f'Picks de tarjetas: {len(cards_picks)}')
print(f'Picks de córners: {len(corners_picks)}')
"
```

### Cron Job (Automatización)
```bash
# Ejecutar cada 6 horas
0 */6 * * * /path/to/daily_update.sh
```

## Manejo de Errores

### API Key No Configurada
```
⚠️ ADVERTENCIA: API_KEY no configurada
📝 Configura la variable de entorno FOOTBALL_API_KEY
💡 Ejemplo: export FOOTBALL_API_KEY='tu_clave_aqui'
```

### Sin Conexión a Internet
```
❌ Error de conexión: [Errno 11001] getaddrinfo failed
🔧 Verifica tu conexión a internet
```

### API Key Inválida
```
❌ Error de API: Invalid API key
🔧 Verifica tu API_KEY en https://apifootball.com/
```

### Sin Partidos Disponibles
```
📭 No se encontraron partidos
💡 Verifica las fechas y IDs de liga
```

## Beneficios de la Integración

### 🎯 Datos en Tiempo Real
- Partidos actualizados diariamente
- Cuotas reales de casas de apuestas
- Estado de partidos en vivo

### 🌍 Cobertura Global
- Todas las ligas principales de Europa
- Competiciones UEFA (Champions, Europa, Conference)
- Flexibilidad para añadir nuevas ligas

### 🤖 Integración Automática
- Los bots detectan automáticamente nuevos datos
- Sin cambios necesarios en el código existente
- Compatibilidad con el sistema actual

### 📊 Mejores Predicciones
- Datos reales vs simulados
- Cuotas actuales del mercado
- Información de árbitros actualizada

## Monitoreo y Logs

### Logs de Conexión
```
🔄 Obteniendo partidos de liga 3 desde 2025-07-22 hasta 2025-07-29...
✅ 13 partidos obtenidos
```

### Logs de Guardado
```
💾 PARTIDOS GUARDADOS
📁 Archivo: live_matches_20250722.json
📊 Total partidos: 45
🏆 Distribución por competición:
  • Champions League: 13 partidos
  • Premier League: 10 partidos
  • La Liga: 8 partidos
  ...
```

### Logs de Integración
```
📁 Archivos de partidos encontrados: 3
   • live_matches_20250722.json
   • champions_league_matches_20250722.json
   • real_matches_20250717.json
✅ live_matches_20250722.json: 45 partidos
🌍 Total de partidos cargados: 82
```

## Próximos Pasos

1. **Configurar API Key** - Obtener y configurar tu clave de API
2. **Instalar Dependencias** - `pip install requests`
3. **Ejecutar Script** - `python3 fetch_live_matches.py`
4. **Verificar Integración** - Comprobar que los bots usan los nuevos datos
5. **Automatizar** - Configurar cron job para actualizaciones automáticas

## Soporte

Para problemas con la integración:
1. Verificar API key y conexión
2. Comprobar logs de error
3. Validar formato de fechas (YYYY-MM-DD)
4. Confirmar IDs de liga correctos

Con esta integración, tendrás acceso a **partidos reales y actualizados** para maximizar la efectividad de tus bots de predicción.