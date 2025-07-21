# 🤖 Bot de Córners - Documentación Técnica

## 📊 Análisis Sofisticado de Córners

El **Bot de Córners** implementa un sistema avanzado de análisis que va mucho más allá de simples promedios. Considera múltiples factores para generar predicciones precisas y confiables.

## 🎯 Metodología de Análisis

### 1. **Estadísticas por Condición de Juego**

El bot mantiene estadísticas separadas para cada equipo según juegue como:

#### **🏠 Equipo Local:**
- **Córners a favor**: Promedio de córners que consigue cuando juega en casa
- **Córners en contra**: Promedio de córners que concede cuando juega en casa

#### **✈️ Equipo Visitante:**
- **Córners a favor**: Promedio de córners que consigue cuando juega fuera
- **Córners en contra**: Promedio de córners que concede cuando juega fuera

### 2. **Análisis Específico del Rival**

Para cada partido, el bot calcula:

```python
# Para el equipo local:
córners_esperados = (córners_promedio_local_casa + córners_promedio_rival_concede_fuera) / 2

# Para el equipo visitante:
córners_esperados = (córners_promedio_visitante_fuera + córners_promedio_rival_concede_casa) / 2
```

### 3. **Factores de Ajuste**

#### **Factor de Estilo de Juego:**
- **Equipos Ofensivos** (+10%): Barcelona, Real Madrid, Real Betis
- **Equipos Defensivos** (-10%): Atletico Madrid
- **Equipos Neutros**: Sin ajuste

#### **Factor de Forma:**
- Basado en resultados recientes (simulado actualmente)
- Rango: -10% a +10%

#### **Factor de Rivalidad:**
- **Derbis** (+15%): Real Madrid vs Atletico Madrid
- **Partidos normales**: Sin ajuste

## 📈 Ejemplo de Análisis Real

### **Caso: Real Madrid (Local) vs Barcelona (Visitante)**

#### **Paso 1: Estadísticas Base**
```
Real Madrid (Local):
- Córners a favor: 7.2/partido
- Córners en contra: 3.4/partido

Barcelona (Visitante):
- Córners a favor: 6.1/partido  
- Córners en contra: 4.2/partido
```

#### **Paso 2: Cálculo por Equipo**
```
Real Madrid esperados: (7.2 + 4.2) / 2 = 5.7 córners
Barcelona esperados: (6.1 + 3.4) / 2 = 4.75 córners
Total base: 10.45 córners
```

#### **Paso 3: Aplicar Factores**
```
Factor estilo: 1.2 (ambos equipos ofensivos)
Factor forma: 1.05 (buena forma reciente)
Factor rivalidad: 1.0 (no es derbi)

Total ajustado: 10.45 × 1.2 × 1.05 = 13.2 córners
```

#### **Paso 4: Calcular Confianza**
```
Base: 60%
+ Datos disponibles: +15%
+ Rango típico: +10%
+ Muchos córners: +15%
= Confianza: 90%
```

## 🔧 Configuración del Bot

### **Parámetros Configurables:**

```json
{
  "confidence_threshold": 70,    // Confianza mínima para apostar
  "min_corners": 9,             // Mínimo de córners para apostar
  "min_odds": 1.5,              // Cuota mínima aceptable
  "max_picks_per_day": 999      // Sin límite - TODOS los que tengan valor
}
```

### **Criterios de Selección:**

Un partido se selecciona para apostar si:
1. **Predicción total** ≥ `min_corners` (9 córners)
2. **Confianza** ≥ `confidence_threshold` (70%)
3. **Cuota estimada** ≥ `min_odds` (1.5)
4. **SIN LÍMITE DIARIO** - Se envían TODOS los picks que cumplan criterios

## 📊 Ejemplo de Salida del Bot

```
🏟️ ANÁLISIS DE CÓRNERS: Real Madrid vs Barcelona

📊 PREDICCIÓN TOTAL: 13.2 córners
🏠 Real Madrid: 5.7 córners esperados
✈️ Barcelona: 4.8 córners esperados

📈 ANÁLISIS POR EQUIPO:
• Real Madrid (local): 7.2 córners/partido, Barcelona concede 4.2 de visitante
• Barcelona (visitante): 6.1 córners/partido, Real Madrid concede 3.4 de local

🔍 FACTORES ADICIONALES:
• Factor de estilo: 1.20
• Factor de forma: 1.05
• Factor de rivalidad: 1.00

💡 RECOMENDACIÓN:
✅ OVER 9.5 córners - Predicción favorable
🔥 Partido con alta expectativa de córners
```

## 🎯 Ventajas del Sistema

### **1. Análisis Contextual**
- Considera la condición de local/visitante
- Analiza el rival específico, no solo promedios generales
- Ajusta según estilos de juego diferentes

### **2. Factores Múltiples**
- Estilo de juego (ofensivo vs defensivo)
- Forma reciente de los equipos
- Rivalidades especiales (derbis)
- Consistencia histórica

### **3. Control de Calidad**
- Sistema de confianza basado en múltiples criterios
- Límites configurables para gestión de riesgo
- Selección automática de mejores oportunidades

### **4. Transparencia**
- Análisis detallado de cada predicción
- Explicación de factores considerados
- Trazabilidad completa del proceso

## 🔄 Actualización de Datos

### **Método `update_team_stats()`**

Permite actualizar las estadísticas con nuevos partidos:

```python
bot.update_team_stats('Real Madrid', {
    'is_home': True,
    'corners_for': 8,
    'corners_against': 3
})
```

### **Mantenimiento Automático**
- Solo mantiene los últimos 10 partidos por condición
- Elimina automáticamente datos antiguos
- Asegura relevancia de las estadísticas

## 📈 Métricas de Rendimiento

El bot proporciona métricas detalladas:

- **Picks generados**: Número de predicciones por día
- **Confianza promedio**: Media de confianza de las predicciones
- **Precisión**: % de aciertos históricos
- **ROI**: Retorno de inversión estimado

## 🚀 Integración con el Sistema

### **API Endpoint: `/api/bot-corneres`**

Retorna predicciones en formato JSON:

```json
{
  "home_team": "Real Madrid",
  "away_team": "Barcelona", 
  "predicted_total": 13.2,
  "confidence": 90,
  "odds": 1.4,
  "analysis": "Análisis detallado...",
  "competition": "La Liga",
  "match_time": "2025-01-22 20:00"
}
```

### **Configuración desde Panel Web**

El bot se integra completamente con el panel de configuración:
- Ajuste de umbrales en tiempo real
- Visualización de estadísticas
- Control de activación/desactivación

## 🎯 Casos de Uso Específicos

### **Configuración Conservadora**
```
Umbral confianza: 80%
Mínimo córners: 11
Cuota mínima: 1.8
→ Pocos picks, alta precisión
```

### **Configuración Agresiva**
```
Umbral confianza: 60%
Mínimo córners: 8
Cuota mínima: 1.4
→ Más picks, menor precisión
```

### **Configuración Balanceada**
```
Umbral confianza: 70%
Mínimo córners: 9
Cuota mínima: 1.6
→ Equilibrio óptimo
```

## 🔮 Futuras Mejoras

1. **Integración con APIs reales** para datos en tiempo real
2. **Machine Learning** para optimizar factores de ajuste
3. **Análisis de weather** y condiciones del campo
4. **Estadísticas de árbitros** y su influencia en córners
5. **Análisis de lesiones** y alineaciones esperadas

---

**Nota**: Este bot representa un enfoque sofisticado y realista para el análisis de córners en fútbol, considerando múltiples variables que realmente afectan el número de córners en un partido.