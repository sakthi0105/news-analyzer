# 📰 News Analyzer - AI-Powered Sentiment Analysis

**Professional dual-agent system for analyzing company news sentiment with real-time stock data**

---

## 🎯 Features

- 🤖 **Dual-Agent Architecture** - Separate data collection and serving agents
- 📊 **Real-Time Stock Prices** - Live data from Finnhub API
- 🧠 **AI Sentiment Analysis** - NLTK VADER sentiment scoring
- 📰 **Trusted News Sources** - Top 50 articles from Bloomberg, Reuters, WSJ, etc.
- 💾 **Persistent Database** - SQLite storage for historical analysis
- 🎨 **Clean Professional UI** - Modern, responsive interface
- 📈 **Complete Analysis** - View all articles with filtering options

---

## 🚀 Quick Start

### Prerequisites
- Python 3.9+
- Internet connection

### Installation

1. **Create project folder:**
```bash
mkdir NewsAnalyzer
cd NewsAnalyzer
```

2. **Create virtual environment:**
```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Mac/Linux
source venv/bin/activate
```

3. **Install dependencies:**
```bash
pip install -r requirements.txt
```

4. **Get API Keys (Free):**

**SerpApi** (Required):
- Sign up: https://serpapi.com/
- Get API key (100 searches/month free)

**Finnhub** (Optional - demo key included):
- Sign up: https://finnhub.io/register
- Get API key (60 calls/minute free)

5. **Set environment variables:**
```bash
# Windows CMD
set SERPAPI_KEY=your_serpapi_key
set FINNHUB_KEY=your_finnhub_key

# Windows PowerShell
$env:SERPAPI_KEY="your_serpapi_key"
$env:FINNHUB_KEY="your_finnhub_key"

# Mac/Linux
export SERPAPI_KEY=your_serpapi_key
export FINNHUB_KEY=your_finnhub_key
```

6. **Run the application:**
```bash
python agent2_server.py
```

7. **Open browser:**
```
http://127.0.0.1:5000
```

---

## 📁 Project Structure

```
NewsAnalyzer/
├── requirements.txt          # Python dependencies
├── database.py              # Database management
├── agent1_collector.py      # Data collection agent
├── agent2_server.py         # Web server agent (main)
├── README.md                # This file
├── news_analyzer.db         # SQLite database (auto-created)
└── templates/
    ├── index.html          # Home page
    └── results.html        # Results page
```

---

## 💡 Usage

### Web Interface

1. Enter a company name (e.g., "Tesla", "Apple", "Microsoft")
2. Click "Analyze News Sentiment"
3. View results:
   - Real-time stock price
   - Top 3 positive news
   - Top 3 negative news
   - All analyzed articles with filters

### Command Line

```bash
# Run Agent 1 directly
python agent1_collector.py Tesla
```

---

## 🛠️ Technologies

| Technology | Purpose |
|------------|---------|
| **Python 3.9+** | Programming language |
| **Flask** | Web framework |
| **SQLite** | Database |
| **NLTK VADER** | Sentiment analysis |
| **SerpApi** | Google News search |
| **Finnhub** | Stock market data |

---

## 📊 Database Schema

**companies** - Company names and metadata
**stock_data** - Historical stock prices
**news_articles** - News with sentiment scores
**analysis_history** - Analysis summaries

---

## 🔐 Security

- Never commit API keys
- Use environment variables
- Demo Finnhub key is for testing only
- Get your own keys for production

---

## 🐛 Troubleshooting

**"SERPAPI_KEY not set"**
- Set environment variable before running
- Check: `echo %SERPAPI_KEY%` (Windows) or `echo $SERPAPI_KEY%` (Mac/Linux)

**"No stock data"**
- Company might not be publicly traded
- Try using stock symbol (e.g., "AAPL" not "Apple")
- Check Finnhub API key

**"No news found"**
- Check SerpApi key is valid
- Verify API credits remaining
- Try a more well-known company

---

## 🚀 Future Enhancements

- [ ] Historical trend charts
- [ ] Company comparison
- [ ] Email alerts
- [ ] Export to CSV/PDF
- [ ] Social media sentiment
- [ ] Mobile app

---

## 📝 License

MIT License - Free to use and modify

---

## 👨‍💻 Author

Created with ❤️ for data-driven decision making

---

## 🙏 Credits

- [SerpApi](https://serpapi.com/) - News data
- [Finnhub](https://finnhub.io/) - Stock data
- [NLTK](https://www.nltk.org/) - Sentiment analysis
- [Flask](https://flask.palletsprojects.com/) - Web framework

---

**⭐ Star this project if you find it useful!**