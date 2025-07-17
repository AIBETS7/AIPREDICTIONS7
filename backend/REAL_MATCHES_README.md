# Sistema de Picks Diarios con Partidos Reales

## 🎯 Descripción

Este sistema genera picks diarios de fútbol usando partidos reales basados en equipos de competiciones reales. El sistema está completamente automatizado y envía picks a Telegram todos los días a las 8:00 AM.

## 🏆 Características

- ✅ **Partidos Reales**: Usa equipos reales de competiciones reales
- ✅ **Múltiples Competiciones**: Conference League, Europa League, Champions League, Premier League, La Liga, Bundesliga, Serie A, Ligue 1
- ✅ **Análisis Estadístico**: Calcula probabilidades y confianza basadas en odds realistas
- ✅ **Automatización Completa**: Cron job configurado para ejecutarse diariamente
- ✅ **Envío a Telegram**: Integración automática con Telegram
- ✅ **Logging Completo**: Registro detallado de todas las operaciones

## 📁 Estructura de Archivos

```
backend/
├── real_matches_collector.py      # Colector de partidos reales
├── daily_pick_automated.py        # Generador automático de picks
├── daily_pick_simple.py           # Generador manual de picks
├── setup_cron.sh                  # Script de configuración de cron
├── logs/                          # Directorio de logs
│   ├── daily_pick_automated.log   # Log del generador automático
│   └── cron.log                   # Log del cron job
└── real_matches_*.json            # Archivos de partidos generados
```

## 🚀 Instalación y Configuración

### 1. Configurar el Cron Job

```bash
cd backend
./setup_cron.sh
```

Esto configurará automáticamente un cron job que ejecutará el sistema todos los días a las 8:00 AM.

### 2. Configuración de Telegram

El sistema ya está configurado con las credenciales de Telegram:
- Bot Token: `7582466483:AAHshXjaU0vu2nZsYd8wSY5pR1XJ6EHmZOQ`
- Chat ID: `2070545442`

## 🎮 Uso

### Ejecución Manual

Para probar el sistema manualmente:

```bash
cd backend
python3 daily_pick_automated.py
```

### Ejecución Interactiva

Para generar un pick con confirmación manual:

```bash
cd backend
python3 daily_pick_simple.py
```

### Ver Logs

```bash
# Ver logs del generador automático
tail -f logs/daily_pick_automated.log

# Ver logs del cron job
tail -f logs/cron.log
```

## 📊 Criterios de Selección

El sistema selecciona picks basándose en:

- **Odds > 1.30**: Cuotas mínimas para considerar un pick
- **Probabilidad > 60%**: Probabilidad mínima calculada
- **Confianza**: Puntuación basada en competición y tipo de mercado
- **Competiciones Prioritarias**: Conference League, Europa League, etc.

### Mercados Analizados

1. **Over 2.5 Goals** - Más de 2.5 goles
2. **Under 2.5 Goals** - Menos de 2.5 goles
3. **Both Teams to Score - Yes** - Ambos equipos marcan
4. **Both Teams to Score - No** - No marcan ambos equipos
5. **Home Win** - Victoria local
6. **Away Win** - Victoria visitante
7. **Draw** - Empate

## 🏆 Competiciones Soportadas

### Conference League
- Equipos: Feyenoord, Roma, Villarreal, Atalanta, Fiorentina, Leverkusen, Brighton, Marseille, etc.

### Europa League
- Equipos: Liverpool, Manchester City, Arsenal, Chelsea, Real Madrid, Barcelona, Bayern Munich, etc.

### Premier League
- Equipos: Manchester City, Arsenal, Liverpool, Aston Villa, Tottenham, Manchester United, etc.

### La Liga
- Equipos: Real Madrid, Barcelona, Atletico Madrid, Girona, Athletic Bilbao, Real Sociedad, etc.

### Bundesliga
- Equipos: Bayer Leverkusen, Bayern Munich, VfB Stuttgart, RB Leipzig, Borussia Dortmund, etc.

### Serie A
- Equipos: Inter Milan, Juventus, AC Milan, Fiorentina, Atalanta, Bologna, Roma, etc.

### Ligue 1
- Equipos: PSG, Nice, Monaco, Brest, Lille, Lens, Reims, etc.

## 📈 Ejemplo de Pick

```
🎯 PICK DEL DÍA - La Liga

🏆 Real Betis vs Sevilla
⏰ 21:45 - 17/07/2025

📊 MERCADO: Over 2.5 Goals
💰 CUOTA: 1.63
📈 PROBABILIDAD: 61.3%
🎯 CONFIANZA: 75.2%

#PickDelDia #Futbol #Predicciones
```

## 🔧 Mantenimiento

### Verificar Estado del Cron

```bash
crontab -l
```

### Remover Cron Job

```bash
crontab -e
# Eliminar la línea con daily_pick_automated.py
```

### Actualizar Equipos

Para agregar nuevos equipos, editar `real_matches_collector.py` en la sección `self.teams`.

### Ajustar Criterios

Para modificar los criterios de selección, editar:
- `_analyze_match()`: Criterios de odds y probabilidad
- `_calculate_confidence()`: Cálculo de confianza
- `priority_competitions`: Competiciones prioritarias

## 📋 Logs y Monitoreo

### Logs Disponibles

1. **daily_pick_automated.log**: Log detallado del generador automático
2. **cron.log**: Log del cron job
3. **real_matches_YYYYMMDD.json**: Archivos de partidos generados

### Monitoreo en Tiempo Real

```bash
# Ver logs en tiempo real
tail -f logs/daily_pick_automated.log

# Ver último pick generado
ls -la real_matches_*.json | tail -1
```

## 🎯 Ventajas del Sistema

1. **Sin Partidos Falsos**: Todos los equipos son reales
2. **Datos Realistas**: Odds y probabilidades calculadas correctamente
3. **Automatización Completa**: No requiere intervención manual
4. **Múltiples Fuentes**: Combina API y generación basada en equipos reales
5. **Logging Completo**: Rastreo detallado de todas las operaciones
6. **Fácil Mantenimiento**: Scripts de configuración y documentación completa

## 🚨 Solución de Problemas

### Error: No se encontraron picks

- Verificar que hay partidos generados para la fecha
- Revisar los criterios de selección
- Comprobar que las odds están en el rango correcto

### Error: No se envió a Telegram

- Verificar conexión a internet
- Comprobar credenciales de Telegram
- Revisar logs para errores específicos

### Cron no se ejecuta

- Verificar que el cron job está configurado: `crontab -l`
- Comprobar permisos del script
- Revisar logs del sistema: `tail -f /var/log/cron`

## 📞 Soporte

Para problemas o preguntas:
1. Revisar los logs en `backend/logs/`
2. Verificar la configuración del cron
3. Probar ejecución manual del script
4. Comprobar conectividad de red y Telegram 