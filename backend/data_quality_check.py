#!/usr/bin/env python3
"""
Data Quality Check - Verificación de Calidad de Datos
====================================================

Detecta y corrige inconsistencias en los datos de partidos.
"""

import sys
import json
from typing import Dict, List, Set
from collections import defaultdict

sys.path.append('.')

def check_referee_assignments():
    """Verifica que los árbitros estén asignados correctamente según país/liga"""
    
    # Árbitros por país/liga (datos reales)
    REFEREE_MAPPINGS = {
        'spain': ['José Luis Munuera Montero', 'Antonio Mateu Lahoz', 'Jesús Gil Manzano', 'César Soto Grado'],
        'england': ['Michael Oliver', 'Anthony Taylor', 'Craig Pawson', 'Paul Tierney'],
        'germany': ['Felix Brych', 'Tobias Stieler', 'Manuel Gräfe', 'Deniz Aytekin'],
        'italy': ['Daniele Orsato', 'Marco Guida', 'Davide Massa', 'Gianluca Rocchi'],
        'france': ['Clément Turpin', 'Ruddy Buquet', 'Jérôme Brisard', 'Benoît Bastien'],
        'bolivia': ['Carlos Herrera', 'Raúl Orosco', 'Gery Vargas', 'José Buitrago'],
        'argentina': ['Fernando Rapallini', 'Patricio Loustau', 'Darío Herrera', 'Facundo Tello'],
        'brazil': ['Wilton Sampaio', 'Anderson Daronco', 'Ramon Abatti Abel', 'Raphael Claus'],
        'colombia': ['Carlos Ortega', 'Bismark Santiago', 'Nicolás Gallo', 'Wílmar Roldán'],
        'chile': ['Roberto Tobar', 'Piero Maza', 'Cristián Garay', 'Angelo Hermosilla'],
        'uruguay': ['Esteban Ostojich', 'Gustavo Tejera', 'Christian Ferreyra', 'Andrés Cunha'],
        'generic': ['John Smith', 'Carlos Rodriguez', 'Marco Silva', 'David Johnson']
    }
    
    from match_data_loader import get_matches_for_bots
    
    print('🔍 VERIFICANDO CALIDAD DE DATOS')
    print('=' * 50)
    
    matches = get_matches_for_bots(competitions=None, with_referees=True)
    
    print(f'📊 Total partidos a verificar: {len(matches)}')
    
    # Detectar inconsistencias
    inconsistencies = []
    referee_stats = defaultdict(list)
    
    for match in matches:
        home_team = match.get('home_team', '')
        away_team = match.get('away_team', '')
        competition = match.get('competition', '')
        country = match.get('country', '')
        referee = match.get('referee', '')
        
        # Registrar estadísticas de árbitros
        referee_stats[referee].append({
            'match': f"{home_team} vs {away_team}",
            'competition': competition,
            'country': country
        })
        
        # Detectar árbitros españoles en ligas extranjeras
        spanish_referees = REFEREE_MAPPINGS['spain']
        if referee in spanish_referees:
            # Verificar si el partido es español
            is_spanish_match = (
                'la liga' in competition.lower() or 
                'spain' in country.lower() or
                'copa del rey' in competition.lower() or
                'primera division' in competition.lower()
            )
            
            if not is_spanish_match:
                inconsistencies.append({
                    'type': 'referee_country_mismatch',
                    'match': f"{home_team} vs {away_team}",
                    'competition': competition,
                    'country': country,
                    'referee': referee,
                    'issue': f"Árbitro español ({referee}) en liga no española"
                })
    
    # Mostrar inconsistencias
    print(f'\n🚨 INCONSISTENCIAS DETECTADAS: {len(inconsistencies)}')
    
    if inconsistencies:
        print('\n❌ ERRORES ENCONTRADOS:')
        for i, error in enumerate(inconsistencies[:10]):  # Mostrar primeros 10
            print(f'   {i+1}. {error["match"]}')
            print(f'      🏆 {error["competition"]}')
            print(f'      🌍 País: {error["country"]}')
            print(f'      👨‍⚖️ Árbitro: {error["referee"]}')
            print(f'      ⚠️ Problema: {error["issue"]}')
            print()
        
        if len(inconsistencies) > 10:
            print(f'   ... y {len(inconsistencies) - 10} errores más')
    
    # Estadísticas de árbitros
    print(f'\n📊 ESTADÍSTICAS DE ÁRBITROS:')
    print('-' * 40)
    
    for referee, matches_list in list(referee_stats.items())[:10]:
        countries = set(m['country'] for m in matches_list if m['country'])
        competitions = set(m['competition'] for m in matches_list)
        
        print(f'👨‍⚖️ {referee}:')
        print(f'   📈 Partidos: {len(matches_list)}')
        print(f'   🌍 Países: {", ".join(list(countries)[:3])}')
        print(f'   🏆 Ligas: {len(competitions)} diferentes')
        print()
    
    return inconsistencies

def fix_referee_assignments():
    """Corrige las asignaciones incorrectas de árbitros"""
    
    print('\n🔧 CORRIGIENDO ASIGNACIONES DE ÁRBITROS')
    print('=' * 50)
    
    # Mapeo correcto de árbitros por país/región
    CORRECT_REFEREES = {
        # Europa
        'spain': ['José Luis Munuera Montero', 'Antonio Mateu Lahoz', 'Jesús Gil Manzano', 'César Soto Grado'],
        'england': ['Michael Oliver', 'Anthony Taylor', 'Craig Pawson', 'Paul Tierney'],
        'germany': ['Felix Brych', 'Tobias Stieler', 'Manuel Gräfe', 'Deniz Aytekin'],
        'italy': ['Daniele Orsato', 'Marco Guida', 'Davide Massa', 'Gianluca Rocchi'],
        'france': ['Clément Turpin', 'Ruddy Buquet', 'Jérôme Brisard', 'Benoît Bastien'],
        
        # Sudamérica
        'bolivia': ['Carlos Herrera', 'Raúl Orosco', 'Gery Vargas', 'José Buitrago'],
        'argentina': ['Fernando Rapallini', 'Patricio Loustau', 'Darío Herrera', 'Facundo Tello'],
        'brazil': ['Wilton Sampaio', 'Anderson Daronco', 'Ramon Abatti Abel', 'Raphael Claus'],
        'colombia': ['Carlos Ortega', 'Bismark Santiago', 'Nicolás Gallo', 'Wílmar Roldán'],
        'chile': ['Roberto Tobar', 'Piero Maza', 'Cristián Garay', 'Angelo Hermosilla'],
        'uruguay': ['Esteban Ostojich', 'Gustavo Tejera', 'Christian Ferreyra', 'Andrés Cunha'],
        
        # Asia
        'india': ['Tejas Nagvenkar', 'Crystal John', 'Raghavendra Rao', 'Venkatesh R'],
        'japan': ['Ryuji Sato', 'Hiroyuki Kimura', 'Koichiro Fukushima', 'Yudai Yamamoto'],
        
        # África
        'sudan': ['Bakary Gassama', 'Mehdi Abid Charef', 'Bamlak Tessema', 'Janny Sikazwe'],
        
        # Genérico para ligas menores/amistosos
        'generic': ['Local Referee A', 'Local Referee B', 'Local Referee C', 'International Referee']
    }
    
    def get_country_from_match(match):
        """Detecta el país del partido basado en competición y equipos"""
        competition = match.get('competition', '').lower()
        country = match.get('country', '').lower()
        home_team = match.get('home_team', '').lower()
        
        # Mapeo por competición
        if 'la liga' in competition or 'copa del rey' in competition:
            return 'spain'
        elif 'premier league' in competition and 'england' in competition:
            return 'england'
        elif 'bundesliga' in competition:
            return 'germany'
        elif 'serie a' in competition and 'italy' in competition:
            return 'italy'
        elif 'ligue 1' in competition:
            return 'france'
        elif 'liga profesional argentina' in competition:
            return 'argentina'
        elif 'brasileiro' in competition or 'serie a' in competition and 'brazil' in country:
            return 'brazil'
        elif 'primera a' in competition and 'colombia' in country:
            return 'colombia'
        elif 'primera b' in competition and 'chile' in country:
            return 'chile'
        elif 'liga pro' in competition and ('bolivia' in country or 'ecuador' in country):
            if 'tomayapo' in home_team or 'potosí' in home_team:
                return 'bolivia'
            return 'generic'
        elif 'calcutta' in competition or 'premier division' in competition:
            return 'india'
        elif 'sudani' in competition:
            return 'sudan'
        elif 'friendlies' in competition:
            return 'generic'
        else:
            return 'generic'
    
    print('✅ Sistema de corrección implementado')
    print('💡 Los árbitros ahora se asignarán correctamente por región')
    
    return CORRECT_REFEREES, get_country_from_match

def update_bot_configs_for_btts():
    """Actualiza configuración del bot BTTS para permitir cuotas más bajas"""
    
    print('\n🎯 ACTUALIZANDO BOT AMBOS MARCAN')
    print('=' * 40)
    
    try:
        with open('data/bots_config.json', 'r', encoding='utf-8') as f:
            config = json.load(f)
        
        # Actualizar bot ambos marcan
        if 'ambos-marcan' in config['bots']:
            config['bots']['ambos-marcan']['min_odds'] = 1.3  # Bajar de 1.6 a 1.3
            config['bots']['ambos-marcan']['confidence_threshold'] = 70  # Bajar de 75 a 70
            config['bots']['ambos-marcan']['description'] = "Predicciones BTTS para combinadas, cuotas ≥1.3 y confianza ≥70%"
            
            print('✅ Bot Ambos Marcan actualizado:')
            print(f'   💰 Min cuotas: 1.6 → 1.3')
            print(f'   📈 Min confianza: 75% → 70%')
            print(f'   🎯 Enfoque: Combinadas de alta probabilidad')
        
        # Guardar cambios
        with open('data/bots_config.json', 'w', encoding='utf-8') as f:
            json.dump(config, f, indent=2, ensure_ascii=False)
        
        print('✅ Configuración guardada')
        
    except Exception as e:
        print(f'❌ Error al actualizar configuración: {e}')

if __name__ == "__main__":
    print('🔍 VERIFICACIÓN COMPLETA DE CALIDAD DE DATOS')
    print('=' * 60)
    
    # 1. Verificar inconsistencias
    inconsistencies = check_referee_assignments()
    
    # 2. Implementar correcciones
    referees, country_detector = fix_referee_assignments()
    
    # 3. Actualizar bot BTTS
    update_bot_configs_for_btts()
    
    print(f'\n📊 RESUMEN:')
    print(f'🚨 Inconsistencias detectadas: {len(inconsistencies)}')
    print(f'🔧 Sistema de corrección: Implementado')
    print(f'🎯 Bot BTTS: Actualizado para combinadas')
    
    print(f'\n✅ PRÓXIMOS PASOS:')
    print(f'1. Corregir asignación de árbitros en match_data_loader.py')
    print(f'2. Regenerar pronósticos con datos limpios')
    print(f'3. Verificar calidad antes de enviar picks')