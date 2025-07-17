#!/usr/bin/env python3
"""
Check football-data.org API status and key validity
"""

import requests
import json

def check_api_status():
    """Check the status of football-data.org API"""
    
    # Your API key
    api_key = "bee404aa9b1149e7b1572ccf2bbbca92"
    
    # Test different endpoints
    endpoints = [
        ("Competitions", "http://api.football-data.org/v2/competitions"),
        ("Matches", "http://api.football-data.org/v2/matches"),
        ("Teams", "http://api.football-data.org/v2/teams/1"),
        ("Free endpoint", "http://api.football-data.org/v2/competitions/2000"),
    ]
    
    headers = {
        'X-Auth-Token': api_key,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'
    }
    
    print("🔍 Checking football-data.org API status...")
    print(f"API Key: {api_key}")
    print("-" * 50)
    
    for name, url in endpoints:
        try:
            print(f"Testing {name}: {url}")
            response = requests.get(url, headers=headers, timeout=10)
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                data = response.json()
                print(f"✅ Success! Response length: {len(str(data))} characters")
                if 'count' in data:
                    print(f"   Items found: {data.get('count', 'N/A')}")
            elif response.status_code == 400:
                error_data = response.json()
                print(f"❌ Error 400: {error_data.get('message', 'Unknown error')}")
                print(f"   Error Code: {error_data.get('errorCode', 'N/A')}")
            elif response.status_code == 403:
                print("❌ Error 403: Forbidden - API key may be invalid or expired")
            elif response.status_code == 429:
                print("⚠️ Error 429: Rate limit exceeded")
            else:
                print(f"❌ Error {response.status_code}: {response.text[:100]}")
            
            print()
            
        except Exception as e:
            print(f"❌ Exception: {e}")
            print()
    
    # Test without API key (free tier)
    print("Testing free tier (without API key)...")
    try:
        response = requests.get("http://api.football-data.org/v2/competitions/2000", timeout=10)
        print(f"Status Code: {response.status_code}")
        if response.status_code == 200:
            print("✅ Free tier works!")
        else:
            print(f"❌ Free tier error: {response.text[:100]}")
    except Exception as e:
        print(f"❌ Exception: {e}")

def get_new_api_key_info():
    """Provide information about getting a new API key"""
    print("\n" + "="*60)
    print("🔑 INFORMACIÓN SOBRE OBTENER UNA NUEVA API KEY")
    print("="*60)
    print()
    print("1. Ve a: https://www.football-data.org/")
    print("2. Haz clic en 'Get API Key' o 'Sign Up'")
    print("3. Crea una cuenta gratuita")
    print("4. Activa tu API key en tu perfil")
    print("5. Copia la nueva API key")
    print()
    print("📋 Límites de la API gratuita:")
    print("   - 10 requests por minuto")
    print("   - Acceso limitado a datos")
    print("   - Algunas competiciones pueden requerir plan de pago")
    print()
    print("🔄 Para actualizar la API key en el sistema:")
    print("   - Edita real_matches_collector.py")
    print("   - Cambia la línea: self.api_key = 'tu_nueva_clave'")
    print()

if __name__ == "__main__":
    check_api_status()
    get_new_api_key_info() 