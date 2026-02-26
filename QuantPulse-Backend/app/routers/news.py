"""
News Sentiment Router

This module provides endpoints for fetching news and computing sentiment analysis
for NSE stocks using NewsAPI and TextBlob.

Sentiment Analysis Approach:
1. Fetch recent news articles related to the stock/company
2. Analyze headline + description using TextBlob
3. Compute average sentiment polarity (-1 to +1)
4. Map to discrete labels (Very Bad → Very Good)
5. Calculate confidence based on sentiment strength and article count

IMPORTANT: This is a prototype-level implementation.
Sentiment analysis is based on general NLP and should NOT be used
for actual trading decisions.
"""

from fastapi import APIRouter, HTTPException, Path, Query
from datetime import datetime, timedelta
from textblob import TextBlob
import httpx
from typing import Optional
from app.config import NEWSAPI_KEY

# Create router for news sentiment endpoints
router = APIRouter(
    prefix="/news-sentiment",
    tags=["News Sentiment"],
)

# =============================================================================
# NewsAPI Configuration
# =============================================================================
NEWSAPI_BASE_URL = "https://newsapi.org/v2/everything"

# =============================================================================
# Company Name Mapping
# =============================================================================
# Maps stock symbols to company names for better news search results

COMPANY_NAMES = {
    "RELIANCE": "Reliance Industries",
    "TCS": "Tata Consultancy Services",
    "INFY": "Infosys",
    "HDFCBANK": "HDFC Bank",
    "ICICIBANK": "ICICI Bank",
    "HINDUNILVR": "Hindustan Unilever",
    "SBIN": "State Bank of India",
    "BHARTIARTL": "Bharti Airtel",
    "ITC": "ITC Limited",
    "KOTAKBANK": "Kotak Mahindra Bank",
    "LT": "Larsen and Toubro",
    "AXISBANK": "Axis Bank",
    "ASIANPAINT": "Asian Paints",
    "MARUTI": "Maruti Suzuki",
    "SUNPHARMA": "Sun Pharmaceutical",
    "TITAN": "Titan Company",
    "ULTRACEMCO": "UltraTech Cement",
    "BAJFINANCE": "Bajaj Finance",
    "WIPRO": "Wipro",
    "ONGC": "Oil and Natural Gas Corporation",
    "NTPC": "NTPC Limited",
    "POWERGRID": "Power Grid Corporation",
    "TATAMOTORS": "Tata Motors",
    "TATASTEEL": "Tata Steel",
    "JSWSTEEL": "JSW Steel",
    "TECHM": "Tech Mahindra",
    "HCLTECH": "HCL Technologies",
    "ADANIENT": "Adani Enterprises",
    "ADANIPORTS": "Adani Ports",
}


def get_company_name(symbol: str) -> str:
    """
    Get the full company name for a stock symbol.
    Falls back to the symbol itself if not found.
    """
    return COMPANY_NAMES.get(symbol.upper(), symbol.upper())


def analyze_sentiment(text: str) -> float:
    """
    Analyze sentiment of a text using TextBlob.
    TextBlob returns a polarity score between -1 (negative) and +1 (positive).
    """
    if not text or not text.strip():
        return 0.0
    
    blob = TextBlob(text)
    return blob.sentiment.polarity


def map_sentiment_to_label(score: float) -> str:
    """
    Map a sentiment score to a discrete label.
    Ranges tuned for financial news.
    """
    if score <= -0.50:
        return "Very Bad"
    elif score <= -0.15:
        return "Bad"
    elif score <= 0.15:
        return "Neutral"
    elif score <= 0.50:
        return "Good"
    else:
        return "Very Good"


def calculate_confidence(avg_sentiment: float, article_count: int) -> int:
    """
    Calculate a confidence score based on sentiment strength and article count.
    """
    if article_count == 0:
        return 0
    
    # Base confidence from sentiment strength (0 to 100)
    sentiment_strength = abs(avg_sentiment) * 100
    
    # Article count multiplier (1.0 to 1.5)
    # Having 5+ articles gives maximum multiplier
    article_multiplier = min(article_count / 5, 1.5)
    
    # Calculate raw confidence
    raw_confidence = sentiment_strength * article_multiplier
    
    # Apply minimum threshold and cap
    confidence = max(10, min(100, raw_confidence))
    
    # If sentiment is very neutral, reduce confidence
    if abs(avg_sentiment) < 0.05:
        confidence = min(confidence, 50)
    
    return int(confidence)


async def fetch_news_articles(query: str, days_back: int = 7) -> list:
    """
    Fetch news articles from NewsAPI asynchronously using HTTPX.
    """
    if not NEWSAPI_KEY:
        print("Warning: NEWSAPI_KEY not found in environment variables")
        return []

    # Calculate date range
    to_date = datetime.now()
    from_date = to_date - timedelta(days=days_back)
    
    params = {
        "q": query,
        "language": "en",
        "sortBy": "relevancy",
        "from": from_date.strftime("%Y-%m-%d"),
        "to": to_date.strftime("%Y-%m-%d"),
        "pageSize": 20,  # Limit to 20 articles
        "apiKey": NEWSAPI_KEY,
    }
    
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(NEWSAPI_BASE_URL, params=params, timeout=10.0)
            
            if response.status_code != 200:
                print(f"NewsAPI error: {response.status_code} - {response.text}")
                return []
                
            data = response.json()
            
            if data.get("status") == "ok":
                return data.get("articles", [])
            else:
                print(f"NewsAPI error: {data.get('message', 'Unknown error')}")
                return []
            
    except Exception as e:
        print(f"Error fetching news: {e}")
        return []


@router.get("/{symbol}")
async def get_news_sentiment(
    symbol: str = Path(..., pattern=r"^[A-Z0-9\.]+$", description="Stock symbol (e.g. TCS, RELIANCE)"),
    days: int = Query(7, ge=1, le=30, description="Days to look back")
):
    """
    Fetch news and compute sentiment analysis for a stock symbol.
    """
    try:
        # Get company name for better search results
        company_name = get_company_name(symbol)
        
        # Build search query
        # Include both company name and "India" or "NSE" for relevance
        search_query = f'"{company_name}" AND (India OR NSE OR stock OR shares)'
        
        # Fetch news articles (Async call)
        articles = await fetch_news_articles(search_query, days)
        
        # If no articles found, try a simpler query
        if not articles:
            articles = await fetch_news_articles(company_name, days)
        
        # Analyze sentiment for each article
        sentiments = []
        analyzed_articles = []
        
        for article in articles:
            title = article.get("title", "") or ""
            description = article.get("description", "") or ""
            
            # Combine title and description for analysis
            combined_text = f"{title}. {description}"
            
            if combined_text.strip():
                sentiment_score = analyze_sentiment(combined_text)
                sentiments.append(sentiment_score)
                
                analyzed_articles.append({
                    "title": title[:100] + "..." if len(title) > 100 else title,
                    "sentiment": round(sentiment_score, 3),
                    "source": article.get("source", {}).get("name", "Unknown"),
                    "publishedAt": article.get("publishedAt", ""),
                })
        
        # Calculate average sentiment
        if sentiments:
            avg_sentiment = sum(sentiments) / len(sentiments)
        else:
            avg_sentiment = 0.0
        
        # Map to discrete label
        sentiment_label = map_sentiment_to_label(avg_sentiment)
        
        # Calculate confidence
        confidence = calculate_confidence(avg_sentiment, len(sentiments))
        
        # Build response
        response = {
            "symbol": symbol.upper(),
            "companyName": company_name,
            "sentimentScore": round(avg_sentiment, 3),
            "sentimentLabel": sentiment_label,
            "newsConfidence": confidence,
            "articlesAnalyzed": len(sentiments),
            "daysAnalyzed": days,
            "timestamp": datetime.now().isoformat(),
            
            # Include sample of analyzed articles (first 5)
            "sampleArticles": analyzed_articles[:5],
            
            # Disclaimer for transparency
            "disclaimer": "Sentiment analysis is based on NLP and should not be used as the sole basis for investment decisions.",
        }
        
        return response

    except Exception as e:
        # Log the full error internally
        print(f"Internal error processing news sentiment for {symbol}: {str(e)}")
        # Return generic error to client
        raise HTTPException(
            status_code=500,
            detail="An internal error occurred while processing sentiment analysis."
        )


@router.get("/test/mock")
async def get_mock_sentiment():
    """
    Test endpoint that returns mock sentiment data.
    Use this to test the frontend without requiring a NewsAPI key.
    """
    return {
        "symbol": "RELIANCE",
        "companyName": "Reliance Industries",
        "sentimentScore": 0.25,
        "sentimentLabel": "Good",
        "newsConfidence": 65,
        "articlesAnalyzed": 12,
        "daysAnalyzed": 7,
        "timestamp": datetime.now().isoformat(),
        "sampleArticles": [
            {
                "title": "Reliance Industries reports strong quarterly results...",
                "sentiment": 0.45,
                "source": "Economic Times",
                "publishedAt": "2026-02-01T10:30:00Z"
            },
            {
                "title": "Jio continues to gain market share in telecom sector...",
                "sentiment": 0.32,
                "source": "Business Standard",
                "publishedAt": "2026-02-01T08:15:00Z"
            },
        ],
        "disclaimer": "This is mock data for testing purposes.",
    }
