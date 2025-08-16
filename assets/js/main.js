(function(){
  // URL de tu backend en Render — ya puesta aquí:
  const API_BASE = window.__API_BASE__ || 'https://myfootballpredictions.onrender.com';
  const sample = {
    ai_stats: {models_accuracy: 87.3, data_points: 124567, win_rate: 72.1, roi: 13.4, updates_per_hour: 2, last_update: new Date().toISOString()},
    bots: [
      {name: 'CornersMaster', bot_type: 'corners', description: 'Especialista en córners', win_rate: 71.4, total_predictions: 1423, roi: 11.2},
      {name: 'CardsGuard', bot_type: 'cards', description: 'Especialista en tarjetas', win_rate: 68.9, total_predictions: 980, roi: 9.1},
      {name: 'BothScorePro', bot_type: 'both_score', description: 'Hace focus en ambos marcan', win_rate: 74.2, total_predictions: 2103, roi: 15.9}
    ],
    recent_predictions: [
      {home_team:'Real Madrid', away_team:'Barcelona', match_date: new Date().toISOString(), league:'La Liga', bot:{name:'BothScorePro'}, prediction_value:'Ambos marcan', odds:'2.10', confidence:87},
      {home_team:'Atletico', away_team:'Valencia', match_date: new Date().toISOString(), league:'La Liga', bot:{name:'CornersMaster'}, prediction_value:'Más de 9 córners', odds:'1.85', confidence:79}
    ]
  };

  // Intenta obtener datos del backend; si falla, usa "sample" (datos de ejemplo)
  function fetchData() {
    return fetch(API_BASE + '/api/site-data.json', {cache:'no-store'})
      .then(r=>{ if(!r.ok) throw new Error('no backend'); return r.json(); })
      .catch(()=>sample);
  }

  function render(stats){
    // actualiza los números de la UI
    if(document.getElementById('acc')) document.getElementById('acc').textContent = stats.ai_stats.models_accuracy.toFixed(1) + '%';
    if(document.getElementById('dp')) document.getElementById('dp').textContent = new Intl.NumberFormat().format(stats.ai_stats.data_points);
    if(document.getElementById('win')) document.getElementById('win').textContent = stats.ai_stats.win_rate.toFixed(1) + '%';
    if(document.getElementById('roi')) document.getElementById('roi').textContent = stats.ai_stats.roi.toFixed(1) + '%';

    const live = stats.recent_predictions && stats.recent_predictions[0];
    if(live && document.getElementById('live-match')){
      document.getElementById('live-match').textContent = live.home_team + ' vs ' + live.away_team;
    }
    if(live && document.getElementById('live-prediction-detail')){
      document.getElementById('live-prediction-detail').textContent = (live.prediction_value || '—') + ' · ' + (live.confidence || 0) + '% · ' + (live.odds || '—');
    }

    const botsList = document.getElementById('bots-list');
    if(botsList){
      botsList.innerHTML = '';
      (stats.bots || []).forEach(b=>{
        const el = document.createElement('div'); el.className='bot-card';
        el.innerHTML = `<h4>${b.name}</h4><p>${(b.bot_type||'').replace('_',' ')} • ${b.description||''}</p><p>${(b.win_rate||0).toFixed(1)}% acierto · ${b.total_predictions||0} pred.</p><p>${(b.roi||0).toFixed(1)}% ROI</p>`;
        botsList.appendChild(el);
      });
    }

    const preds = document.getElementById('predictions-list');
    if(preds){
      preds.innerHTML = '';
      if(stats.recent_predictions && stats.recent_predictions.length){
        stats.recent_predictions.forEach(p=>{
          const d = new Date(p.match_date);
          const item = document.createElement('div'); item.className='card';
          item.innerHTML = `<strong>${p.home_team} vs ${p.away_team}</strong><div>${d.toLocaleString()} · ${p.league}</div><div>${p.bot.name} · ${p.prediction_value} · ${p.odds} · ${p.confidence}%</div>`;
          preds.appendChild(item);
        });
      } else preds.textContent='No hay predicciones disponibles';
    }
  }

  fetchData().then(render).catch(err=>{
    console.error(err); render(sample);
  });
})();
