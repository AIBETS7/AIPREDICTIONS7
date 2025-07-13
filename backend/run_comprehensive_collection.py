#!/usr/bin/env python3
"""
Run comprehensive data collection from all football websites
"""

import sys
import os
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from comprehensive_data_collector import ComprehensiveDataCollector
from loguru import logger

def main():
    logger.info("Starting comprehensive data collection from all football websites...")
    
    try:
        collector = ComprehensiveDataCollector()
        collector.run_comprehensive_collection()
        
        logger.info("✅ Comprehensive data collection completed successfully!")
        logger.info("📊 Data from WhoScored, BDFutbol, Soccerway, Resultados-Futbol, FootballDatabase, and FCStats has been collected and stored in the database.")
        logger.info("🤖 Your AI now has access to comprehensive match data for better pick evaluation!")
        
    except Exception as e:
        logger.error(f"❌ Error during comprehensive data collection: {e}")

if __name__ == "__main__":
    main() 