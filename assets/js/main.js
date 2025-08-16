// Cargar datos desde el backend en Render
fetch('https://myfootballpredictions.onrender.com/api/site-data.json')
  .then(response => response.json())
  .then(data => {
    console.log("Datos recibidos:", data);

    // Mostrar estadísticas
    const statsDiv = document.getElementById("stats");
    if (statsDiv) {
      statsDiv.innerHTML = `
        <p>Precisión modelos: ${data.ai_stats.models_accuracy}%</p>
        <p>Win Rate: ${data.ai_stats.win_rate}%</p>
        <p>ROI: ${data.ai_stats.roi}%</p>
        <p>Última actualización: ${data.ai_stats.last_update}</p>
      `;
    }

    // Mostrar bots
    const botsDiv = document.getElementById("bots");
    if (botsDiv) {
      botsDiv.innerHTML = data.bots.map(bot => `
        <div>
          <h3>${bot.name}</h3>
          <p>${bot.description}</p>
          <p>Win rate: ${bot.win_rate}% | ROI: ${bot.roi}%</p>
        </div>
      `).join("");
    }

    // Mostrar predicciones recientes
    const predsDiv = document.getElementById("predictions");
    if (predsDiv) {
      predsDiv.innerHTML = data.recent_predictions.map(pred => `
        <div>
          <strong>${pred.home_team} vs ${pred.away_team}</strong> (${pred.league})<br>
          Bot: ${pred.bot.name} → ${pred.prediction_value} | Cuota: ${pred.odds} | Confianza: ${pred.confidence}%
        </div>
      `).join("<hr>");
    }
  })
  .catch(err => console.error("Error cargando datos:", err));
