import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time

def scrape_with_retry(scraper_func, max_retries=3):
    """Retry a scraper function if it fails"""
    for attempt in range(max_retries):
        try:
            articles = scraper_func()
            if articles:
                return articles
            print(f"  Attempt {attempt + 1}: No articles returned")
        except Exception as e:
            print(f"  Attempt {attempt + 1} failed: {e}")
            if attempt < max_retries - 1:
                time.sleep(2)
    return []

def scrape_bleeping_computer():
    """Scrape latest cybersecurity news from Bleeping Computer"""
    url = "https://www.bleepingcomputer.com/"
    
    print(f"Fetching {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    
    article_cards = soup.find_all('div', class_='bc_latest_news_text')[:5]
    
    for card in article_cards:
        try:
            link_tag = card.find('a')
            if link_tag:
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href', '')
                
                if link and not link.startswith('http'):
                    link = 'https://www.bleepingcomputer.com' + link
                
                desc_tag = card.find('p')
                description = desc_tag.get_text(strip=True) if desc_tag else "No description"
                
                articles.append({
                    'title': title,
                    'link': link,
                    'description': description[:200],
                    'source': 'Bleeping Computer'
                })
        except Exception as e:
            print(f"Error parsing Bleeping Computer article: {e}")
            continue
    
    print(f"✓ Bleeping Computer: {len(articles)} articles")
    return articles

def scrape_wired_security():
    """Scrape security news from WIRED"""
    url = "https://www.wired.com/tag/security/"
    
    print(f"Fetching {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    
    article_items = soup.find_all('div', class_='summary-item')[:5]
    
    for item in article_items:
        try:
            title_tag = item.find('h3')
            if title_tag:
                link_tag = title_tag.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    if link and not link.startswith('http'):
                        link = 'https://www.wired.com' + link
                    
                    desc_tag = item.find('p', class_='summary-item__dek')
                    description = desc_tag.get_text(strip=True) if desc_tag else "No description"
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description[:200],
                        'source': 'WIRED'
                    })
        except Exception as e:
            print(f"Error parsing WIRED article: {e}")
            continue
    
    print(f"✓ WIRED: {len(articles)} articles")
    return articles

def scrape_ars_technica_security():
    """Scrape security news from Ars Technica"""
    url = "https://arstechnica.com/security/"
    
    print(f"Fetching {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    
    article_items = soup.find_all('article')[:5]
    
    for item in article_items:
        try:
            title_tag = item.find('h2')
            if title_tag:
                link_tag = title_tag.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    if link and not link.startswith('http'):
                        link = 'https://arstechnica.com' + link
                    
                    desc_tag = item.find('p', class_='excerpt')
                    description = desc_tag.get_text(strip=True) if desc_tag else "No description"
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description[:200],
                        'source': 'Ars Technica'
                    })
        except Exception as e:
            print(f"Error parsing Ars Technica article: {e}")
            continue
    
    print(f"✓ Ars Technica: {len(articles)} articles")
    return articles

def scrape_krebs_security():
    """Scrape news from Krebs on Security"""
    url = "https://krebsonsecurity.com/"
    
    print(f"Fetching {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    articles = []
    
    article_items = soup.find_all('article', class_='post')[:5]
    
    for item in article_items:
        try:
            title_tag = item.find('h2', class_='entry-title')
            if title_tag:
                link_tag = title_tag.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    desc_tag = item.find('div', class_='entry-content')
                    if desc_tag:
                        p_tag = desc_tag.find('p')
                        description = p_tag.get_text(strip=True) if p_tag else "No description"
                    else:
                        description = "No description"
                    
                    articles.append({
                        'title': title,
                        'link': link,
                        'description': description[:200],
                        'source': 'Krebs on Security'
                    })
        except Exception as e:
            print(f"Error parsing Krebs article: {e}")
            continue
    
    print(f"✓ Krebs on Security: {len(articles)} articles")
    return articles

def scrape_darknet_diaries():
    """Scrape latest episodes from Darknet Diaries"""
    url = "https://darknetdiaries.com/episode/"
    
    print(f"Fetching {url}...")
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    }
    response = requests.get(url, headers=headers, timeout=10)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.content, 'html.parser')
    episodes = []
    
    episode_headers = soup.find_all('h2')[:3]
    
    for h2 in episode_headers:
        try:
            link_tag = h2.find('a')
            if link_tag:
                title = link_tag.get_text(strip=True)
                link = link_tag.get('href', '')
                
                if link and not link.startswith('http'):
                    link = 'https://darknetdiaries.com' + link
                
                parent = h2.parent
                desc_tag = parent.find('p') if parent else None
                description = desc_tag.get_text(strip=True) if desc_tag else "No description"
                
                date_tag = parent.find('time') if parent else None
                date = date_tag.get_text(strip=True) if date_tag else ""
                
                episodes.append({
                    'title': title,
                    'link': link,
                    'description': description[:250],
                    'date': date,
                    'source': 'Darknet Diaries'
                })
                print(f"  Found: {title}")
        except Exception as e:
            print(f"Error parsing Darknet Diaries episode: {e}")
            continue
    
    print(f"✓ Darknet Diaries: {len(episodes)} episodes")
    return episodes

def scrape_all_sources():
    """Scrape all cybersecurity news sources with retry logic"""
    print("\n" + "="*50)
    print("Starting multi-source scrape with retry logic...")
    print("="*50 + "\n")
    
    all_articles = []
    
    # Scrape each source with retry
    all_articles.extend(scrape_with_retry(scrape_bleeping_computer))
    all_articles.extend(scrape_with_retry(scrape_wired_security))
    all_articles.extend(scrape_with_retry(scrape_ars_technica_security))
    all_articles.extend(scrape_with_retry(scrape_krebs_security))
    
    print(f"\n{'='*50}")
    print(f"Total articles scraped: {len(all_articles)}")
    print(f"{'='*50}\n")
    
    return all_articles

if __name__ == "__main__":
    news = scrape_all_sources()
    
    if news:
        print("\nARTICLES FOUND:")
        print("="*50 + "\n")
        
        for i, article in enumerate(news, 1):
            print(f"{i}. [{article['source']}] {article['title']}")
            print(f"   {article['link']}")
            print(f"   {article['description']}\n")
