#!/usr/bin/env python3
"""
Test script to get tomorrow's matches from Flashscore and Sofascore
"""

import os
from datetime import datetime, timedelta
from loguru import logger
from scrapers.flashscore_scraper import FlashScoreScraper
from scrapers.sofascore_scraper import SofaScoreScraper

def test_tomorrow_matches():
    """Test getting tomorrow's matches"""
    tomorrow = datetime.now() + timedelta(days=1)
    tomorrow_str = tomorrow.strftime('%Y-%m-%d')
    
    print(f"Testing matches for tomorrow: {tomorrow_str}")
    print("=" * 60)
    
    # Test Flashscore
    print("\n🔍 Testing Flashscore...")
    try:
        flashscore = FlashScoreScraper()
        
        # Test general football tomorrow
        url = f"https://www.flashscore.com/football/tomorrow/"
        print(f"URL: {url}")
        
        response = flashscore._make_request(url)
        print(f"✅ Flashscore response: {response.status_code}")
        
        # Parse matches
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors
        match_containers = soup.find_all('div', class_='event__match')
        if not match_containers:
            match_containers = soup.find_all('div', class_='event__match--static')
        if not match_containers:
            match_containers = soup.find_all('div', class_='event__match--scheduled')
        
        print(f"Found {len(match_containers)} match containers")
        
        # Look for Conference League specifically
        conference_matches = []
        for container in match_containers:
            try:
                # Check if it's Conference League
                competition_elem = container.find_parent('div', class_='event__title')
                if competition_elem:
                    competition_text = competition_elem.get_text(strip=True).lower()
                    if 'conference' in competition_text:
                        print(f"Found Conference League match: {competition_text}")
                        conference_matches.append(container)
            except:
                continue
        
        print(f"Found {len(conference_matches)} Conference League matches")
        
    except Exception as e:
        print(f"❌ Flashscore error: {e}")
    
    # Test Sofascore
    print("\n🔍 Testing Sofascore...")
    try:
        sofascore = SofaScoreScraper()
        
        # Test general football tomorrow
        url = f"https://www.sofascore.com/tournament/football/tomorrow"
        print(f"URL: {url}")
        
        response = sofascore._make_request(url)
        print(f"✅ Sofascore response: {response.status_code}")
        
        # Parse matches
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Try multiple selectors
        match_containers = soup.find_all('div', class_='sc-fqkvVR')
        if not match_containers:
            match_containers = soup.find_all('div', class_='sc-jQrLum')
        if not match_containers:
            match_containers = soup.find_all('div', class_='sc-eCssSg')
        
        print(f"Found {len(match_containers)} match containers")
        
        # Look for Conference League specifically
        conference_matches = []
        for container in match_containers:
            try:
                # Check if it's Conference League
                competition_elem = container.find_parent('div', class_='sc-dcJsrY')
                if competition_elem:
                    competition_text = competition_elem.get_text(strip=True).lower()
                    if 'conference' in competition_text:
                        print(f"Found Conference League match: {competition_text}")
                        conference_matches.append(container)
            except:
                continue
        
        print(f"Found {len(conference_matches)} Conference League matches")
        
    except Exception as e:
        print(f"❌ Sofascore error: {e}")

if __name__ == "__main__":
    test_tomorrow_matches() 