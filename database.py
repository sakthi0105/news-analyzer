"""
Database Management System for News Analyzer
Handles all SQLite database operations
"""

import sqlite3
from datetime import datetime

class NewsDatabase:
    def __init__(self, db_name='news_analyzer.db'):
        self.db_name = db_name
        self.init_db()
    
    def get_connection(self):
        """Get database connection"""
        return sqlite3.connect(self.db_name)
    
    def init_db(self):
        """Initialize database with required tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Create companies table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS companies (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Create stock_data table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS stock_data (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                symbol TEXT,
                price REAL,
                change REAL,
                change_percent REAL,
                day_high REAL,
                day_low REAL,
                market_cap TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')
        
        # Create news_articles table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS news_articles (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                title TEXT NOT NULL,
                link TEXT,
                snippet TEXT,
                source TEXT,
                sentiment_score REAL,
                sentiment_category TEXT,
                fetched_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')
        
        # Create analysis_history table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS analysis_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_id INTEGER NOT NULL,
                total_articles INTEGER,
                positive_count INTEGER,
                negative_count INTEGER,
                neutral_count INTEGER,
                avg_sentiment REAL,
                analyzed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (company_id) REFERENCES companies (id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def insert_company(self, company_name):
        """Insert company and return its ID"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT id FROM companies WHERE name = ?', (company_name,))
        result = cursor.fetchone()
        
        if result:
            company_id = result[0]
        else:
            cursor.execute('INSERT INTO companies (name) VALUES (?)', (company_name,))
            company_id = cursor.lastrowid
            conn.commit()
        
        conn.close()
        return company_id
    
    def insert_stock_data(self, company_id, stock_data):
        """Insert stock data for a company"""
        if not stock_data:
            return None
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO stock_data 
            (company_id, symbol, price, change, change_percent, day_high, day_low, market_cap)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?)
        ''', (
            company_id,
            stock_data.get('symbol'),
            stock_data.get('price'),
            stock_data.get('change'),
            stock_data.get('change_percent'),
            stock_data.get('day_high'),
            stock_data.get('day_low'),
            str(stock_data.get('market_cap'))
        ))
        
        stock_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return stock_id
    
    def insert_news_articles(self, company_id, articles):
        """Insert multiple news articles"""
        if not articles:
            return []
        
        conn = self.get_connection()
        cursor = conn.cursor()
        
        article_ids = []
        for article in articles:
            cursor.execute('''
                INSERT INTO news_articles 
                (company_id, title, link, snippet, source, sentiment_score, sentiment_category)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            ''', (
                company_id,
                article.get('title'),
                article.get('link'),
                article.get('snippet'),
                article.get('source'),
                article.get('sentiment_score'),
                article.get('sentiment_category')
            ))
            article_ids.append(cursor.lastrowid)
        
        conn.commit()
        conn.close()
        return article_ids
    
    def insert_analysis_summary(self, company_id, summary):
        """Insert analysis summary"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO analysis_history 
            (company_id, total_articles, positive_count, negative_count, neutral_count, avg_sentiment)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            company_id,
            summary.get('total_articles'),
            summary.get('positive_count'),
            summary.get('negative_count'),
            summary.get('neutral_count'),
            summary.get('avg_sentiment')
        ))
        
        conn.commit()
        conn.close()
    
    def get_latest_stock_data(self, company_name):
        """Get latest stock data for a company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT s.symbol, s.price, s.change, s.change_percent, 
                   s.day_high, s.day_low, s.market_cap, s.fetched_at, c.name
            FROM stock_data s
            JOIN companies c ON s.company_id = c.id
            WHERE c.name = ?
            ORDER BY s.fetched_at DESC
            LIMIT 1
        ''', (company_name,))
        
        result = cursor.fetchone()
        conn.close()
        
        if result:
            market_cap = result[6]
            try:
                if market_cap and market_cap != 'N/A':
                    market_cap = float(market_cap)
            except (ValueError, TypeError):
                market_cap = 'N/A'
            
            return {
                'symbol': result[0],
                'price': result[1],
                'change': result[2],
                'change_percent': result[3],
                'day_high': result[4],
                'day_low': result[5],
                'market_cap': market_cap,
                'fetched_at': result[7],
                'name': result[8]
            }
        return None
    
    def get_latest_news(self, company_name, limit=50):
        """Get latest news articles for a company"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT n.title, n.link, n.snippet, n.source, 
                   n.sentiment_score, n.sentiment_category, n.fetched_at
            FROM news_articles n
            JOIN companies c ON n.company_id = c.id
            WHERE c.name = ?
            ORDER BY n.fetched_at DESC
            LIMIT ?
        ''', (company_name, limit))
        
        results = cursor.fetchall()
        conn.close()
        
        articles = []
        for row in results:
            articles.append({
                'title': row[0],
                'link': row[1],
                'snippet': row[2],
                'source': row[3],
                'sentiment_score': row[4],
                'sentiment_category': row[5],
                'fetched_at': row[6]
            })
        
        return articles
    
    def get_all_companies(self):
        """Get all companies in database"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT name, created_at FROM companies ORDER BY created_at DESC')
        results = cursor.fetchall()
        conn.close()
        
        return [{'name': row[0], 'created_at': row[1]} for row in results]