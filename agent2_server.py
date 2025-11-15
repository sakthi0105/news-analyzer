"""
AGENT 2: Data Server Agent
Serves data from database to web UI
"""

from flask import Flask, render_template, request, jsonify
from database import NewsDatabase
from agent1_collector import collect_and_store_data
import threading
import os

app = Flask(__name__)
db = NewsDatabase()

@app.route('/')
def index():
    """Home page"""
    companies = db.get_all_companies()
    return render_template('index.html', companies=companies)

@app.route('/analyze', methods=['POST'])
def analyze():
    """Trigger analysis"""
    company_name = request.form.get('company_name', '').strip()
    
    if not company_name:
        return render_template('index.html', error="Please enter a company name")
    
    # Run Agent 1 to collect data
    def collect_in_background():
        collect_and_store_data(company_name)
    
    thread = threading.Thread(target=collect_in_background)
    thread.start()
    thread.join(timeout=30)
    
    return get_results(company_name)

@app.route('/results/<company_name>')
def results(company_name):
    """Show results"""
    return get_results(company_name)

def get_results(company_name):
    """Fetch and display results from database"""
    try:
        # Get stock data
        stock_data = db.get_latest_stock_data(company_name)
        
        # Get news articles
        all_articles = db.get_latest_news(company_name, limit=50)
        
        if not all_articles:
            return render_template('results.html',
                                 company_name=company_name,
                                 stock_data=stock_data,
                                 no_results=True)
        
        # Filter by sentiment (strict thresholds)
        positive_articles = [a for a in all_articles if a['sentiment_score'] > 0.05]
        negative_articles = [a for a in all_articles if a['sentiment_score'] < -0.05]
        neutral_articles = [a for a in all_articles if -0.05 <= a['sentiment_score'] <= 0.05]
        
        # Top 3 of each
        positive_news = sorted(positive_articles, key=lambda x: x['sentiment_score'], reverse=True)[:3]
        negative_news = sorted(negative_articles, key=lambda x: x['sentiment_score'])[:3]
        
        # Statistics
        positive_count = len(positive_articles)
        negative_count = len(negative_articles)
        neutral_count = len(neutral_articles)
        
        return render_template('results.html',
                             company_name=company_name,
                             stock_data=stock_data,
                             positive_news=positive_news,
                             negative_news=negative_news,
                             all_articles=all_articles,
                             total_articles=len(all_articles),
                             positive_count=positive_count,
                             negative_count=negative_count,
                             neutral_count=neutral_count,
                             no_results=False)
    
    except Exception as e:
        return render_template('index.html',
                             error=f"Error: {str(e)}")

@app.route('/refresh/<company_name>')
def refresh(company_name):
    """Refresh data"""
    success, message = collect_and_store_data(company_name)
    if success:
        return get_results(company_name)
    else:
        return render_template('index.html', error=message)

@app.route('/api/companies')
def api_companies():
    """API: Get all companies"""
    companies = db.get_all_companies()
    return jsonify(companies)

@app.route('/api/stock/<company_name>')
def api_stock(company_name):
    """API: Get stock data"""
    stock_data = db.get_latest_stock_data(company_name)
    if stock_data:
        return jsonify(stock_data)
    return jsonify({'error': 'Not found'}), 404

@app.route('/api/news/<company_name>')
def api_news(company_name):
    """API: Get news articles"""
    articles = db.get_latest_news(company_name)
    return jsonify(articles)

if __name__ == '__main__':
    print("\n🤖 AGENT 2: Starting web server...")
    print("🌐 Server running...")
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)