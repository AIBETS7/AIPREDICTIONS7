# 🤖 Panel de Configuración de Bots - AI Predictions 7

## ¿Qué puedes configurar desde aquí?

**¡SÍ! Puedes configurar completamente todos los bots desde el panel web.** El sistema incluye un panel de administración completo que te permite gestionar todos los aspectos de tus bots de predicciones de fútbol.

## 🎯 Características Principales

### ✅ **Gestión Completa de Bots**
- **4 Bots Especializados**: Ambos Marcan, Córners, Empates, y Tarjetas
- **Control Individual**: Configura cada bot por separado
- **Activación/Desactivación**: Enciende o apaga bots específicos
- **Parámetros Personalizables**: Ajusta umbrales, cuotas, y competiciones

### ✅ **Configuraciones Disponibles**

#### **Por Bot Individual:**
- **Umbral de Confianza**: 50% - 95% (qué tan seguro debe estar el bot)
- **Cuotas Mínimas/Máximas**: Rango de cuotas aceptables
- **Competiciones**: Selecciona qué ligas analizar
- **Picks por Día**: Máximo número de predicciones diarias
- **Parámetros Específicos**: 
  - Mínimo de córners (Bot Córners)
  - Mínimo de tarjetas (Bot Tarjetas)

#### **Configuración Global:**
- **Frecuencia de Actualización**: Cada cuántos minutos buscar nuevos partidos
- **Notificaciones Telegram**: Configurar bot y chat ID
- **Límites Globales**: Máximo de picks totales por día
- **Gestión de Bankroll**: Porcentaje máximo de apuesta

### ✅ **Analíticas en Tiempo Real**
- **Estadísticas por Bot**: Picks hoy, precisión, beneficios
- **Métricas Globales**: Rendimiento general del sistema
- **Gráficos de Rendimiento**: Visualización de resultados
- **Historial de Actividad**: Seguimiento de la actividad de cada bot

## 🚀 Cómo Acceder al Panel

### **Opción 1: Desde la Web Principal**
1. Ve a tu página principal: `index.html`
2. Haz clic en **"⚙️ Configurar Bots"** en el menú de navegación
3. Accederás directamente al panel de configuración

### **Opción 2: Acceso Directo**
- Abre directamente: `bot-config.html`

## 🎮 Cómo Usar el Panel

### **1. Controles Globales**
```
▶️ Iniciar Todos los Bots    - Activa todos los bots
⏸️ Pausar Todos los Bots     - Pausa todos los bots  
🔄 Reiniciar Todos los Bots  - Reinicia el sistema
📊 Actualizar Datos         - Refresca información
```

### **2. Gestión Individual de Bots**

#### **Bot Ambos Marcan** 🎯
- **Función**: Encuentra partidos donde ambos equipos marcarán
- **Configuraciones**:
  - Umbral de confianza: 70% (recomendado)
  - Cuota mínima: 1.5
  - Competiciones: La Liga, Premier League, etc.

#### **Bot Córners** ⚽
- **Función**: Predice partidos con muchos córners
- **Configuraciones**:
  - Mínimo de córners: 9
  - Cuota mínima: 1.6
  - Umbral de confianza: 70%

#### **Bot Empates** ⚖️
- **Función**: Identifica partidos con alta probabilidad de empate
- **Configuraciones**:
  - Cuota mínima: 3.0 (los empates tienen cuotas más altas)
  - Picks por día: 2 (más selectivo)

#### **Bot Tarjetas** 🟨
- **Función**: Encuentra partidos con muchas tarjetas
- **Configuraciones**:
  - Mínimo de tarjetas: 4
  - Cuota mínima: 1.7

### **3. Pestañas del Panel**

#### **🤖 Gestión de Bots**
- Configurar parámetros individuales
- Ver estadísticas en tiempo real
- Probar y guardar configuraciones

#### **📊 Analíticas**
- Métricas de rendimiento
- Gráficos de beneficios
- Comparación entre bots

#### **⚙️ Configuración**
- Ajustes globales del sistema
- Configuración de Telegram
- Herramientas avanzadas

## 🔧 Configuración de Telegram

### **Paso 1: Crear Bot de Telegram**
1. Habla con @BotFather en Telegram
2. Usa `/newbot` y sigue las instrucciones
3. Guarda el **Token** que te da

### **Paso 2: Obtener Chat ID**
1. Agrega tu bot a un grupo o úsalo en privado
2. Envía un mensaje al bot
3. Ve a: `https://api.telegram.org/bot<TU_TOKEN>/getUpdates`
4. Busca el `chat_id` en la respuesta

### **Paso 3: Configurar en el Panel**
1. Ve a la pestaña **"⚙️ Configuración"**
2. Ingresa tu **Token Bot Telegram**
3. Ingresa tu **Chat ID**
4. Haz clic en **"📱 Probar Telegram"**

## 📊 Entendiendo las Estadísticas

### **Métricas por Bot:**
- **Picks Hoy**: Cuántas predicciones ha hecho hoy
- **Precisión**: % de aciertos en los últimos 30 días
- **Beneficio**: Ganancia/pérdida en euros (últimos 30 días)

### **Métricas Globales:**
- **Total Picks Hoy**: Suma de todos los bots
- **Precisión Promedio**: Media de precisión de todos los bots
- **Beneficio Total**: Suma de beneficios de todos los bots
- **Bots Activos**: Cuántos bots están funcionando

## 🛠️ Herramientas Avanzadas

### **Exportar/Importar Configuración**
- **Exportar**: Descarga tu configuración como archivo JSON
- **Importar**: Carga una configuración previamente guardada

### **Limpiar Cache**
- Borra datos temporales para resolver problemas

### **Restaurar Valores por Defecto**
- Vuelve a la configuración original del sistema

## 🔄 Automatización

### **El Sistema Funciona Solo**
Una vez configurado:
1. Los bots se ejecutan automáticamente cada 30 minutos (configurable)
2. Analizan partidos de las competiciones seleccionadas
3. Generan picks según tus parámetros
4. Envían notificaciones a Telegram
5. Actualizan estadísticas en tiempo real

### **Configuración Recomendada para Principiantes**
```
Bot Ambos Marcan:
- Confianza: 75%
- Cuota mínima: 1.6
- Picks por día: 3

Bot Córners:
- Confianza: 70%
- Mínimo córners: 9
- Picks por día: 2

Bot Empates:
- Confianza: 80%
- Cuota mínima: 3.2
- Picks por día: 1

Bot Tarjetas:
- Confianza: 75%
- Mínimo tarjetas: 4
- Picks por día: 2
```

## ❓ Resolución de Problemas

### **Si los bots no generan picks:**
1. Verifica que estén **activos** (estado verde)
2. Revisa que el **umbral de confianza** no sea muy alto
3. Comprueba que las **competiciones** seleccionadas estén en temporada

### **Si no llegan notificaciones de Telegram:**
1. Verifica el **Token** y **Chat ID**
2. Usa **"📱 Probar Telegram"** para verificar conexión
3. Asegúrate de que las **notificaciones estén habilitadas**

### **Si hay errores en el panel:**
1. Usa **"🔄 Reiniciar Todos los Bots"**
2. Prueba **"🗑️ Limpiar Cache"**
3. Como último recurso: **"⚠️ Restaurar Valores por Defecto"**

## 🎉 ¡Listo para Usar!

**Tu sistema de bots está completamente configurado y listo para generar predicciones automáticamente.** El panel te da control total sobre todos los aspectos del sistema, desde parámetros individuales hasta configuraciones globales.

**¿Necesitas ayuda?** Todas las funciones tienen tooltips explicativos y el sistema muestra mensajes de confirmación para cada acción.

---

**Nota**: Los endpoints de API están implementados y funcionando. El sistema guarda toda la configuración en `backend/data/bots_config.json` y se actualiza en tiempo real.