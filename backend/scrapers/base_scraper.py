import requests
import time
import random
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from tenacity import retry, stop_after_attempt, wait_exponential
from config.settings import SCRAPING_CONFIG, RATE_LIMITS
from models.data_models import DataSource

USER_AGENTS = [
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
    'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36',
    'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:124.0) Gecko/20100101 Firefox/124.0',
    'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7; rv:123.0) Gecko/20100101 Firefox/123.0',
]
EXTRA_HEADERS = {
    'Referer': 'https://www.google.com/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Cache-Control': 'no-cache',
    'Pragma': 'no-cache',
    'DNT': '1',
    'Sec-Fetch-Dest': 'document',
    'Sec-Fetch-Mode': 'navigate',
    'Sec-Fetch-Site': 'none',
    'Sec-Fetch-User': '?1',
    'Upgrade-Insecure-Requests': '1',
}

class BaseScraper(ABC):
    """Base class for all web scrapers"""
    
    def __init__(self, name: str, base_url: str):
        self.name = name
        self.base_url = base_url
        self.session = requests.Session()
        self.session.headers.update(SCRAPING_CONFIG['headers'])
        self.session.headers['User-Agent'] = SCRAPING_CONFIG['user_agent']
        self.last_request_time = 0
        self.request_count = 0
        self.error_count = 0
        self.success_count = 0
        self.response_times = []
        
    def _rate_limit(self):
        """Implement rate limiting to avoid being blocked"""
        current_time = time.time()
        time_since_last = current_time - self.last_request_time
        
        # Ensure minimum delay between requests
        min_delay = SCRAPING_CONFIG['request_delay']
        if time_since_last < min_delay:
            sleep_time = min_delay - time_since_last
            time.sleep(sleep_time)
        
        # Add some randomness to avoid detection
        random_delay = random.uniform(0.5, 2.0)
        time.sleep(random_delay)
        
        self.last_request_time = time.time()
    
    @retry(stop=stop_after_attempt(3), wait=wait_exponential(multiplier=1, min=4, max=10))
    def _make_request(self, url: str, params: Optional[Dict] = None) -> requests.Response:
        """Make HTTP request with retry logic and anti-blocking headers"""
        self._rate_limit()
        start_time = time.time()
        try:
            # Rotar User-Agent y añadir headers realistas
            headers = SCRAPING_CONFIG['headers'].copy()
            headers['User-Agent'] = random.choice(USER_AGENTS)
            headers.update(EXTRA_HEADERS)
            response = self.session.get(
                url,
                params=params,
                timeout=SCRAPING_CONFIG['timeout'],
                headers=headers
            )
            response.raise_for_status()
            
            # Track response time
            response_time = time.time() - start_time
            self.response_times.append(response_time)
            
            # Keep only last 100 response times
            if len(self.response_times) > 100:
                self.response_times = self.response_times[-100:]
            
            self.success_count += 1
            self.request_count += 1
            
            logger.info(f"{self.name}: Successful request to {url} in {response_time:.2f}s")
            return response
            
        except requests.exceptions.RequestException as e:
            self.error_count += 1
            self.request_count += 1
            logger.error(f"{self.name}: Request failed for {url}: {str(e)}")
            raise
    
    def get_success_rate(self) -> float:
        """Calculate success rate of requests"""
        if self.request_count == 0:
            return 0.0
        return self.success_count / self.request_count
    
    def get_avg_response_time(self) -> float:
        """Calculate average response time"""
        if not self.response_times:
            return 0.0
        return sum(self.response_times) / len(self.response_times)
    
    def get_data_source_status(self) -> DataSource:
        """Get current status of this data source"""
        return DataSource(
            name=self.name,
            url=self.base_url,
            last_scraped=datetime.now(),
            status='active' if self.get_success_rate() > 0.8 else 'error',
            error_count=self.error_count,
            success_rate=self.get_success_rate(),
            response_time_avg=self.get_avg_response_time()
        )
    
    @abstractmethod
    def scrape_matches(self, league_id: str, date_from: datetime, date_to: datetime) -> List[Dict]:
        """Scrape matches for a specific league and date range"""
        pass
    
    @abstractmethod
    def scrape_team_stats(self, team_id: str) -> Dict:
        """Scrape statistics for a specific team"""
        pass
    
    @abstractmethod
    def scrape_h2h(self, team1_id: str, team2_id: str) -> Dict:
        """Scrape head-to-head statistics between two teams"""
        pass
    
    @abstractmethod
    def scrape_odds(self, match_id: str) -> Dict:
        """Scrape odds for a specific match"""
        pass
    
    @abstractmethod
    def scrape_live_match(self, match_id: str) -> Dict:
        """Scrape live match data"""
        pass
    
    def cleanup(self):
        """Clean up resources"""
        self.session.close()
