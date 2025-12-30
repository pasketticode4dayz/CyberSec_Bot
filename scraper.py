import requests
from bs4 import BeautifulSoup
from datetime import datetime

def scrape_darknet_diaries():
    """Scrape latest episodes from Darknet Diaries"""
    url = "https://darknetdiaries.com/episode/"
    
    print(f"Fetching {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        episodes = []
        
        # Find all h2 tags which contain episode titles
        episode_headers = soup.find_all('h2')[:3]  # Get latest 3
        
        for h2 in episode_headers:
            try:
                # Find the link inside h2
                link_tag = h2.find('a')
                if link_tag:
                    title = link_tag.get_text(strip=True)
                    link = link_tag.get('href', '')
                    
                    if link and not link.startswith('http'):
                        link = 'https://darknetdiaries.com' + link
                    
                    # The description is in the paragraph after the h2
                    # Find the parent and then the next paragraph
                    parent = h2.parent
                    desc_tag = parent.find('p') if parent else None
                    description = desc_tag.get_text(strip=True) if desc_tag else "No description"
                    
                    # Also get the date/duration if available
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
    
    except Exception as e:
        print(f"✗ Darknet Diaries error: {e}")
        import traceback
        traceback.print_exc()
        return []

def scrape_bleeping_computer():
    """Scrape latest cybersecurity news from Bleeping Computer"""
    url = "https://www.bleepingcomputer.com/"
    
    print(f"Fetching {url}...")
    
    try:
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
    
    except Exception as e:
        print(f"✗ Bleeping Computer error: {e}")
        return []

def scrape_wired_security():
    """Scrape security news from WIRED"""
    url = "https://www.wired.com/tag/security/"
    
    print(f"Fetching {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # WIRED uses summary-item classes
        article_items = soup.find_all('div', class_='summary-item')[:5]
        
        for item in article_items:
            try:
                # Find title and link
                title_tag = item.find('h3')
                if title_tag:
                    link_tag = title_tag.find('a')
                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        link = link_tag.get('href', '')
                        
                        if link and not link.startswith('http'):
                            link = 'https://www.wired.com' + link
                        
                        # Find description
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
    
    except Exception as e:
        print(f"✗ WIRED error: {e}")
        return []

def scrape_ars_technica_security():
    """Scrape security news from Ars Technica"""
    url = "https://arstechnica.com/security/"
    
    print(f"Fetching {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Ars Technica article structure
        article_items = soup.find_all('article')[:5]
        
        for item in article_items:
            try:
                # Find title
                title_tag = item.find('h2')
                if title_tag:
                    link_tag = title_tag.find('a')
                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        link = link_tag.get('href', '')
                        
                        if link and not link.startswith('http'):
                            link = 'https://arstechnica.com' + link
                        
                        # Find description
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
    
    except Exception as e:
        print(f"✗ Ars Technica error: {e}")
        return []

def scrape_krebs_security():
    """Scrape news from Krebs on Security"""
    url = "https://krebsonsecurity.com/"
    
    print(f"Fetching {url}...")
    
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.content, 'html.parser')
        articles = []
        
        # Krebs uses article tags
        article_items = soup.find_all('article', class_='post')[:5]
        
        for item in article_items:
            try:
                # Find title
                title_tag = item.find('h2', class_='entry-title')
                if title_tag:
                    link_tag = title_tag.find('a')
                    if link_tag:
                        title = link_tag.get_text(strip=True)
                        link = link_tag.get('href', '')
                        
                        # Find description
                        desc_tag = item.find('div', class_='entry-content')
                        if desc_tag:
                            # Get first paragraph
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
    
    except Exception as e:
        print(f"✗ Krebs on Security error: {e}")
        return []

def scrape_all_sources():
    """Scrape all cybersecurity news sources"""
    print("\n" + "="*50)
    print("Starting multi-source scrape...")
    print("="*50 + "\n")
    
    all_articles = []
    
    # Scrape each source
    all_articles.extend(scrape_bleeping_computer())
    all_articles.extend(scrape_wired_security())
    all_articles.extend(scrape_ars_technica_security())
    all_articles.extend(scrape_krebs_security())
    
    print(f"\n{'='*50}")
    print(f"Total articles scraped: {len(all_articles)}")
    print(f"{'='*50}\n")
    
    return all_articles

# Test the scraper
if __name__ == "__main__":
    news = scrape_all_sources()
    
    if news:
        print("\nARTICLES FOUND:")
        print("="*50 + "\n")
        
        for i, article in enumerate(news, 1):
            print(f"{i}. [{article['source']}] {article['title']}")
            print(f"   {article['link']}")
            print(f"   {article['description']}\n")