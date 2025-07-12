#!/usr/bin/env python3
"""
Test script for real matches collector
"""

import sys
import os
from datetime import datetime

# Add backend directory to path
sys.path.append('backend')

try:
    from real_matches_collector import RealMatchesCollector, get_fallback_matches
    
    def test_real_matches():
        print("Testing Real Matches Collector...")
        print("=" * 50)
        
        # Test fallback matches (no API key needed)
        print("\n1. Testing fallback matches:")
        fallback_matches = get_fallback_matches()
        for match in fallback_matches:
            print(f"  - {match['home_team']} vs {match['away_team']} ({match['competition']})")
            print(f"    Time: {match['match_time']}")
            print(f"    Status: {match['status']}")
            print()
        
        # Test real matches collector (if API key is available)
        print("\n2. Testing real matches collector:")
        collector = RealMatchesCollector()
        
        # Check if API key is available
        if collector.api_key != 'your_api_key_here':
            print("  API key found, attempting to fetch real matches...")
            try:
                real_matches = collector.get_todays_matches()
                if real_matches:
                    print(f"  Found {len(real_matches)} real matches:")
                    for match in real_matches[:5]:  # Show first 5
                        print(f"    - {match['home_team']} vs {match['away_team']} ({match['competition']})")
                        print(f"      Time: {match['match_time']}")
                        print(f"      Status: {match['status']}")
                        print()
                else:
                    print("  No real matches found for today")
            except Exception as e:
                print(f"  Error fetching real matches: {e}")
        else:
            print("  No API key found, using fallback data")
            print("  To get real matches, sign up at https://www.api-football.com/")
            print("  and add your API key as an environment variable: API_FOOTBALL_KEY")
        
        print("\n3. Testing prediction generation:")
        from real_daily_pick import RealDailyPickGenerator
        
        generator = RealDailyPickGenerator()
        matches = generator.get_real_matches()
        
        if matches:
            best_match = generator.select_best_match(matches)
            if best_match:
                print(f"  Best match selected: {best_match['home_team']} vs {best_match['away_team']}")
                prediction = generator.generate_prediction(best_match)
                print(f"  Prediction: {prediction['prediction']}")
                print(f"  Confidence: {prediction['confidence']}%")
                print(f"  Reasoning: {prediction['reasoning']}")
            else:
                print("  No suitable matches found for prediction")
        else:
            print("  No matches available for prediction")
        
        print("\n" + "=" * 50)
        print("Test completed!")
        
    if __name__ == "__main__":
        test_real_matches()
        
except ImportError as e:
    print(f"Import error: {e}")
    print("Make sure you're running this from the project root directory")
except Exception as e:
    print(f"Error: {e}") 