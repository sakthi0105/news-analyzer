"""
AGENT 1: Data Collector Agent
Fetches news and stock data, analyzes sentiment, and stores in database
"""

from serpapi import GoogleSearch
import nltk
from nltk.sentiment.vader import SentimentIntensityAnalyzer
import os
import requests
from database import NewsDatabase

# Download VADER lexicon (run once)
try:
    nltk.data.find('sentiment/vader_lexicon.zip')
except LookupError:
    nltk.download('vader_lexicon')

# Initialize sentiment analyzer
sia = SentimentIntensityAnalyzer()

# Initialize database
db = NewsDatabase()

def get_news(company_name):
    """Fetch news articles from trusted sources only"""
    api_key = os.environ.get('SERPAPI_KEY')
    
    if not api_key:
        raise ValueError("SERPAPI_KEY environment variable not set")
    
    # List of trusted, high-quality news sources
    trusted_sources = [
        'bloomberg.com', 'reuters.com', 'wsj.com', 'ft.com',
        'cnbc.com', 'forbes.com', 'businessinsider.com',
        'marketwatch.com', 'theverge.com', 'techcrunch.com',
        'cnn.com', 'bbc.com', 'theguardian.com', 'nytimes.com',
        'washingtonpost.com', 'apnews.com', 'fortune.com',
        'barrons.com', 'economist.com', 'seekingalpha.com',
        'investopedia.com', 'morningstar.com', 'yahoo.com/finance'
    ]
    
    params = {
        "engine": "google",
        "q": company_name,
        "tbm": "nws",
        "api_key": api_key,
        "num": 50,
        "gl": "us",
        "hl": "en"
    }
    
    print(f"🔍 Fetching top 50 news articles for '{company_name}'...")
    
    search = GoogleSearch(params)
    results = search.get_dict()
    
    news_articles = []
    trusted_count = 0
    
    if "news_results" in results:
        for article in results["news_results"]:
            link = article.get("link", "")
            source = article.get("source", "").lower()
            
            # Check if from trusted source
            is_trusted = any(trusted in link.lower() for trusted in trusted_sources)
            if not is_trusted:
                is_trusted = any(trusted.replace('.com', '') in source for trusted in trusted_sources)
            
            if is_trusted:
                news_articles.append({
                    "title": article.get("title", ""),
                    "link": link,
                    "snippet": article.get("snippet", ""),
                    "source": article.get("source", ""),
                    "date": article.get("date", "")
                })
                trusted_count += 1
    
    print(f"✅ Found {trusted_count} articles from trusted sources")
    return news_articles

def get_stock_price(company_name):
    """Get stock price from Finnhub API"""
    try:
        api_key = os.environ.get('FINNHUB_KEY', 'ct76kspr01qnhnd37magct76kspr01qnhnd37mb0')
        
        symbol_map = {
            'apple': 'AAPL', 'microsoft': 'MSFT', 'google': 'GOOGL',
            'alphabet': 'GOOGL', 'amazon': 'AMZN', 'tesla': 'TSLA',
            'meta': 'META', 'facebook': 'META', 'nvidia': 'NVDA',
            'netflix': 'NFLX', 'intel': 'INTC', 'amd': 'AMD',
            'ibm': 'IBM', 'oracle': 'ORCL', 'salesforce': 'CRM',
            'adobe': 'ADBE', 'cisco': 'CSCO', 'paypal': 'PYPL',
            'uber': 'UBER', 'lyft': 'LYFT', 'airbnb': 'ABNB',
            'spotify': 'SPOT', 'snapchat': 'SNAP', 'snap': 'SNAP',
            'zoom': 'ZM', 'disney': 'DIS', 'walmart': 'WMT',
            'starbucks': 'SBUX', 'nike': 'NKE', 'twitter': 'TWTR',
            'coca cola': 'KO', 'cocacola': 'KO', 'pepsi': 'PEP',
            'mcdonalds': 'MCD', 'boeing': 'BA', 'ford': 'F',
            'gm': 'GM', 'general motors': 'GM', 'jp morgan': 'JPM',
            'bank of america': 'BAC', 'visa': 'V', 'mastercard': 'MA',
            'costco': 'COST', 'target': 'TGT', 'pfizer': 'PFE'
        }
        
        symbol = symbol_map.get(company_name.lower().strip(), company_name.upper().strip())
        
        print(f"📈 Fetching stock data for {symbol}...")
        
        quote_url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={api_key}"
        response = requests.get(quote_url, timeout=10)
        
        if response.status_code != 200:
            print(f"⚠️ Stock API error: {response.status_code}")
            return None
        
        data = response.json()
        current_price = data.get('c', 0)
        
        if not current_price or current_price == 0:
            print(f"⚠️ No stock data for {symbol}")
            return None
        
        previous_close = data.get('pc', current_price)
        change = current_price - previous_close
        change_percent = (change / previous_close * 100) if previous_close else 0
        
        # Get company profile
        profile_url = f"https://finnhub.io/api/v1/stock/profile2?symbol={symbol}&token={api_key}"
        profile_response = requests.get(profile_url, timeout=10)
        company_name_full = company_name
        market_cap = 'N/A'
        
        if profile_response.status_code == 200:
            profile = profile_response.json()
            if profile:
                company_name_full = profile.get('name', company_name)
                market_cap = profile.get('marketCapitalization', 'N/A')
                if market_cap != 'N/A' and market_cap:
                    market_cap = market_cap * 1000000
        
        print(f"✅ Stock data retrieved: ${current_price}")
        return {
            'symbol': symbol,
            'name': company_name_full,
            'price': float(current_price),
            'change': float(change),
            'change_percent': float(change_percent),
            'day_high': float(data.get('h', 0)),
            'day_low': float(data.get('l', 0)),
            'market_cap': market_cap
        }
        
    except Exception as e:
        print(f"❌ Error fetching stock: {e}")
        return None

def analyze_sentiment(text):
    """Analyze sentiment using VADER"""
    scores = sia.polarity_scores(text)
    return scores['compound']

def categorize_sentiment(score):
    """Categorize sentiment score"""
    if score > 0.05:
        return 'positive'
    elif score < -0.05:
        return 'negative'
    else:
        return 'neutral'

def collect_and_store_data(company_name):
    """Main collection function"""
    print(f"\n🤖 AGENT 1: Collecting data for '{company_name}'...")
    
    try:
        # Register company
        company_id = db.insert_company(company_name)
        
        # Fetch stock data
        stock_data = get_stock_price(company_name)
        if stock_data:
            db.insert_stock_data(company_id, stock_data)
        
        # Fetch news
        articles = get_news(company_name)
        
        if not articles:
            return False, "No news found"
        
        # Analyze sentiment
        print(f"🧠 Analyzing sentiment for {len(articles)} articles...")
        positive_count = 0
        negative_count = 0
        neutral_count = 0
        total_sentiment = 0
        
        for article in articles:
            text = f"{article['title']} {article['snippet']}"
            score = analyze_sentiment(text)
            category = categorize_sentiment(score)
            
            article['sentiment_score'] = score
            article['sentiment_category'] = category
            
            total_sentiment += score
            if category == 'positive':
                positive_count += 1
            elif category == 'negative':
                negative_count += 1
            else:
                neutral_count += 1
        
        avg_sentiment = total_sentiment / len(articles)
        
        # Store in database
        db.insert_news_articles(company_id, articles)
        
        summary = {
            'total_articles': len(articles),
            'positive_count': positive_count,
            'negative_count': negative_count,
            'neutral_count': neutral_count,
            'avg_sentiment': avg_sentiment
        }
        db.insert_analysis_summary(company_id, summary)
        
        print(f"✅ AGENT 1: Complete! Analyzed {len(articles)} articles\n")
        return True, "Success"
        
    except Exception as e:
        print(f"❌ AGENT 1: Error - {e}\n")
        return False, str(e)

if __name__ == "__main__":
    import sys
    company = sys.argv[1] if len(sys.argv) > 1 else input("Company name: ")
    collect_and_store_data(company)