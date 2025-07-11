#!/usr/bin/env python3
"""
Data Collection Script
Runs the data collector to gather information from various sources
"""

import sys
import os
import time
from datetime import datetime
from loguru import logger

# Add the backend directory to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from data_collector import DataCollector
from config.settings import LOGGING_CONFIG

# Configure logging
logger.add(
    LOGGING_CONFIG['file'],
    level=LOGGING_CONFIG['level'],
    format=LOGGING_CONFIG['format'],
    rotation=LOGGING_CONFIG['rotation'],
    retention=LOGGING_CONFIG['retention']
)

def main():
    """Main function to run data collection"""
    logger.info("Starting data collection process")
    
    collector = DataCollector()
    
    try:
        # Collect data for the last 7 days and next 7 days
        logger.info("Collecting data from all sources...")
        data = collector.collect_all_data(days_back=7, days_forward=7)
        
        # Print summary
        print("\n" + "="*50)
        print("DATA COLLECTION SUMMARY")
        print("="*50)
        print(f"Matches collected: {len(data['matches'])}")
        print(f"Teams data: {len(data['teams'])}")
        print(f"H2H records: {len(data['h2h_records'])}")
        print(f"Odds data: {len(data['odds'])}")
        print(f"Last updated: {data['last_updated']}")
        
        # Print source status
        print("\n" + "="*50)
        print("DATA SOURCE STATUS")
        print("="*50)
        status = collector.get_source_status()
        for source, source_status in status.items():
            print(f"{source.upper()}:")
            print(f"  Status: {source_status.status}")
            print(f"  Success Rate: {source_status.success_rate:.1%}")
            print(f"  Error Count: {source_status.error_count}")
            print(f"  Avg Response Time: {source_status.response_time_avg:.2f}s")
            print()
        
        # Show sample matches
        if data['matches']:
            print("="*50)
            print("SAMPLE MATCHES")
            print("="*50)
            for i, match in enumerate(data['matches'][:5]):
                print(f"{i+1}. {match.get('home_team', 'Unknown')} vs {match.get('away_team', 'Unknown')}")
                print(f"   Status: {match.get('status', 'Unknown')}")
                print(f"   Time: {match.get('time', 'Unknown')}")
                print()
        
        logger.info("Data collection process completed successfully")
        
    except Exception as e:
        logger.error(f"Error in data collection process: {e}")
        print(f"Error: {e}")
        return 1
    
    finally:
        collector.cleanup()
    
    return 0

if __name__ == "__main__":
    exit_code = main()
    sys.exit(exit_code)
