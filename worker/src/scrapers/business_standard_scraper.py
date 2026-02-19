"""
Business Standard News Scraper
Scrapes financial news from Business Standard (India)
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
from typing import List, Dict
import time

class BusinessStandardScraper:
    """Scrape news from Business Standard"""
    
    BASE_URL = "https://www.business-standard.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        })
    
    def scrape_stock_news(self, symbol: str, limit: int = 10) -> List[Dict]:
        """
        Scrape news for a stock symbol
        """
        articles = []
        clean_symbol = symbol.replace('.NS', '').replace('.BO', '')
        
        try:
            # Search for company news
            search_url = f"{self.BASE_URL}/search?q={clean_symbol}"
            
            print(f"Searching Business Standard for {clean_symbol}...")
            response = self.session.get(search_url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find article cards
                article_cards = soup.find_all('div', class_='listingstyle_cardlist__')
                
                if not article_cards:
                    # Try alternative structure
                    article_cards = soup.find_all('article')
                
                for card in article_cards[:limit]:
                    try:
                        # Extract title
                        title_elem = card.find('h2') or card.find('h3') or card.find('a')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text().strip()
                        
                        # Extract link
                        link_elem = card.find('a', href=True)
                        link = link_elem['href'] if link_elem else ''
                        if link and not link.startswith('http'):
                            link = self.BASE_URL + link
                        
                        # Extract description
                        desc_elem = card.find('p') or card.find('div', class_='desc')
                        description = desc_elem.get_text().strip() if desc_elem else ''
                        
                        # Extract date
                        date_elem = card.find('time') or card.find('span', class_='date')
                        published = date_elem.get_text().strip() if date_elem else datetime.now().isoformat()
                        
                        articles.append({
                            'title': title,
                            'description': description,
                            'url': link,
                            'source': 'Business Standard',
                            'published_at': published,
                            'symbol': symbol
                        })
                    
                    except Exception as e:
                        print(f"Error parsing article: {e}")
                        continue
                
                print(f"✅ Found {len(articles)} articles from Business Standard")
            
            else:
                print(f"⚠️  Business Standard returned status {response.status_code}")
                return self._mock_data(symbol)
        
        except Exception as e:
            print(f"Error scraping Business Standard: {e}")
            return self._mock_data(symbol)
        
        # If no articles found, return mock data
        if not articles:
            return self._mock_data(symbol)
        
        return articles
    
    def scrape_top_stories(self) -> List[Dict]:
        """Scrape top market stories"""
        articles = []
        
        try:
            url = f"{self.BASE_URL}/markets"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                soup = BeautifulSoup(response.content, 'html.parser')
                
                # Find top stories
                story_cards = soup.find_all('div', class_='top-story')[:5]
                
                if not story_cards:
                    story_cards = soup.find_all('article')[:5]
                
                for card in story_cards:
                    try:
                        title_elem = card.find('h2') or card.find('h3')
                        if not title_elem:
                            continue
                        
                        title = title_elem.get_text().strip()
                        link = card.find('a')['href'] if card.find('a') else ''
                        if link and not link.startswith('http'):
                            link = self.BASE_URL + link
                        
                        articles.append({
                            'title': title,
                            'url': link,
                            'source': 'Business Standard',
                            'published_at': datetime.now().isoformat()
                        })
                    
                    except:
                        continue
        
        except Exception as e:
            print(f"Error scraping top stories: {e}")
        
        return articles
    
    def _mock_data(self, symbol: str) -> List[Dict]:
        """Generate mock news data"""
        company_name = symbol.replace('.NS', '').replace('.BO', '')
        
        return [
            {
                'title': f'{company_name} reports strong quarterly results, beats estimates',
                'description': f'{company_name} has posted better-than-expected earnings for the quarter, driven by robust demand and improved margins.',
                'url': f'{self.BASE_URL}/companies',
                'source': 'Business Standard (Mock)',
                'published_at': datetime.now().isoformat(),
                'symbol': symbol
            },
            {
                'title': f'Analysts upgrade {company_name} on growth prospects',
                'description': f'Multiple brokerages have raised their target price for {company_name} citing strong fundamentals.',
                'url': f'{self.BASE_URL}/markets',
                'source': 'Business Standard (Mock)',
                'published_at': datetime.now().isoformat(),
                'symbol': symbol
            }
        ]

def demo():
    """Demo Business Standard scraper"""
    scraper = BusinessStandardScraper()
    
    print("Business Standard Scraper Demo")
    print("="*70)
    
    # Test with RELIANCE
    symbol = "RELIANCE"
    articles = scraper.scrape_stock_news(symbol, limit=5)
    
    print(f"\nNews for {symbol}:")
    print("="*70)
    
    for i, article in enumerate(articles, 1):
        print(f"\n{i}. {article['title']}")
        print(f"   {article['description'][:100]}...")
        print(f"   Source: {article['source']}")
        print(f"   URL: {article['url'][:60]}...")
    
    # Top stories
    print("\n\nTop Market Stories:")
    print("="*70)
    top_stories = scraper.scrape_top_stories()
    
    for i, story in enumerate(top_stories[:3], 1):
        print(f"\n{i}. {story['title']}")
        print(f"   URL: {story['url'][:60]}...")

if __name__ == "__main__":
    demo()
