from flask import render_template, request, redirect, url_for, flash, jsonify, session
from app import app, db
from models import User, Subscription, Prediction, BettingBot, ContactMessage
from datetime import datetime, timedelta
import requests
import base64
import json
import logging

# Configurar el idioma por defecto a español
app.config['DEFAULT_LANGUAGE'] = 'es'

@app.route('/')
def index():
    """Panel principal con estadísticas IA y predicciones"""
    # Obtener bots activos con sus estadísticas
    bots = BettingBot.query.filter_by(is_active=True).all()
    
    # Obtener predicciones recientes
    recent_predictions = Prediction.query.filter(
        Prediction.match_date >= datetime.utcnow()
    ).order_by(Prediction.match_date.asc()).limit(10).all()
    
    # Calcular estadísticas generales
    total_predictions = Prediction.query.count()
    won_predictions = Prediction.query.filter_by(status='won').count()
    overall_win_rate = (won_predictions / total_predictions * 100) if total_predictions > 0 else 0
    
    # Estadísticas IA para mostrar
    ai_stats = {
        'models_accuracy': 87.3,
        'data_points': 125000,
        'win_rate': round(overall_win_rate, 1),
        'roi': 15.8,
        'updates_per_hour': 24,
        'last_update': datetime.utcnow().strftime('%H:%M')
    }
    
    return render_template('index.html', 
                         bots=bots, 
                         recent_predictions=recent_predictions,
                         ai_stats=ai_stats)

@app.route('/bot/<bot_type>')
def bot_detail(bot_type):
    """Mostrar predicciones y estadísticas de bot específico"""
    bot = BettingBot.query.filter_by(bot_type=bot_type, is_active=True).first_or_404()
    
    # Obtener predicciones para este bot
    predictions = Prediction.query.filter_by(bot_id=bot.id).filter(
        Prediction.match_date >= datetime.utcnow()
    ).order_by(Prediction.match_date.asc()).limit(20).all()
    
    # Obtener rendimiento histórico
    historical_predictions = Prediction.query.filter_by(bot_id=bot.id).filter(
        Prediction.status.in_(['won', 'lost'])
    ).order_by(Prediction.match_date.desc()).limit(50).all()
    
    template_map = {
        'corners': 'bot_corners.html',
        'cards': 'bot_cards.html',
        'both_score': 'bot_both_score.html',
        'draws': 'bot_draws.html'
    }
    
    template = template_map.get(bot_type, 'bot_corners.html')
    
    return render_template(template, 
                         bot=bot, 
                         predictions=predictions,
                         historical_predictions=historical_predictions)

@app.route('/quick-predict')
def quick_predict():
    """Mobile-optimized quick predictions dashboard"""
    return render_template('quick_predict.html')

@app.route('/contact', methods=['GET', 'POST'])
def contact():
    """Formulario de contacto"""
    if request.method == 'POST':
        name = request.form.get('name')
        email = request.form.get('email')
        subject = request.form.get('subject')
        message = request.form.get('message')
        
        # Crear mensaje de contacto
        contact_msg = ContactMessage(
            name=name,
            email=email,
            subject=subject,
            message=message
        )
        
        db.session.add(contact_msg)
        db.session.commit()
        
        flash('¡Gracias por tu mensaje! Te responderemos pronto.', 'success')
        return redirect(url_for('contact'))
    
    return render_template('contact.html')

@app.route('/subscribe')
def subscribe():
    """Página de suscripción"""
    # Verificar si ya está suscrito
    if session.get('user_id'):
        user = User.query.get(session['user_id'])
        if user and user.is_subscribed:
            flash('Ya tienes una suscripción activa.', 'info')
            return redirect(url_for('index'))
    
    return render_template('subscribe.html')

@app.route('/subscription/success')
def subscription_success():
    """Página de éxito tras suscripción"""
    return render_template('subscription_success.html')

# Eliminar rutas de idioma ya que solo usamos español
# No necesitamos language blueprint ni traducciones dinámicas
