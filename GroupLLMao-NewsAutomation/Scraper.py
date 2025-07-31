import os
from flask import Flask, jsonify
from newspaper import Article
from dotenv import load_dotenv
import requests
from datetime import datetime, timedelta
import re

load_dotenv()
API_KEY = os.getenv("API_KEY")

def calculate_relevance_score(content, keyword):
    """Calculate how relevant the content is to the keyword"""
    keyword_lower = keyword.lower()
    content_lower = content.lower()
    
    # Count keyword occurrences (case-insensitive)
    keyword_count = content_lower.count(keyword_lower)
    
    # Count related terms (you can expand this based on your needs)
    related_terms = {
        'gaza': ['palestine', 'palestinian', 'israel', 'hamas', 'gaza strip'],
        'ukraine': ['russia', 'ukrainian', 'kyiv', 'putin', 'zelensky'],
        'climate': ['global warming', 'carbon', 'emission', 'temperature', 'environment'],
        # Add more topics as needed
    }
    
    related_count = 0
    if keyword_lower in related_terms:
        for term in related_terms[keyword_lower]:
            related_count += content_lower.count(term)
    
    # Simple relevance score
    total_words = len(content.split())
    relevance_score = (keyword_count * 2 + related_count) / max(total_words, 1) * 1000
    
    return relevance_score, keyword_count

def get_relevant_articles(keyword, max_articles=5):
    """Get multiple articles and return the most relevant one"""
    url = f"https://newsdata.io/api/1/news?apikey={API_KEY}&q={keyword}&language=en&size={max_articles}"
    
    try:
        response = requests.get(url, timeout=15)
        data = response.json()
        
        if "results" in data and isinstance(data["results"], list) and data["results"]:
            return data["results"]
        else:
            return []
    except Exception as e:
        print(f"Error fetching articles: {e}")
        return []

def extract_article_content(url):
    """Extract article content with error handling"""
    try:
        article = Article(url)
        article.download()
        article.parse()
        
        # Combine title and content
        full_content = f"{article.title}\n\n{article.text}"
        return full_content, article.title
    except Exception as e:
        print(f"Error extracting content from {url}: {e}")
        return None, None

def filter_relevant_content(content, keyword, max_paragraphs=5):
    """Filter content to only include paragraphs relevant to the topic"""
    if not content:
        return content
    
    paragraphs = content.split('\n\n')
    keyword_lower = keyword.lower()
    
    # Keep title (usually first paragraph)
    relevant_paragraphs = [paragraphs[0]] if paragraphs else []
    
    # Filter paragraphs that contain the keyword or related terms
    for paragraph in paragraphs[1:]:
        if keyword_lower in paragraph.lower() and len(paragraph.strip()) > 50:
            relevant_paragraphs.append(paragraph)
            if len(relevant_paragraphs) >= max_paragraphs:
                break
    
    # If no relevant paragraphs found, return first few paragraphs
    if len(relevant_paragraphs) <= 1 and len(paragraphs) > 1:
        relevant_paragraphs = paragraphs[:3]
    
    return '\n\n'.join(relevant_paragraphs)

def scraper(keyword):
    """Main scraper function with improved topic relevance"""
    articles = get_relevant_articles(keyword, max_articles=5)
    
    if not articles:
        return "No articles found for the specified topic."
    
    best_article = None
    best_score = 0
    best_content = None
    
    # Test multiple articles to find the most relevant one
    for article in articles[:3]:  # Check top 3 articles
        url = article.get("link")
        if not url:
            continue
            
        content, title = extract_article_content(url)
        if not content:
            continue
        
        # Calculate relevance score
        score, keyword_count = calculate_relevance_score(content, keyword)
        
        print(f"Article: {title[:50]}... - Score: {score:.2f}, Keyword mentions: {keyword_count}")
        
        # Must have at least one mention of the keyword
        if keyword_count > 0 and score > best_score:
            best_score = score
            best_article = article
            best_content = content
    
    if best_content:
        # Filter content to focus on relevant paragraphs
        filtered_content = filter_relevant_content(best_content, keyword)
        return filtered_content
    else:
        # Fallback to first article if none are particularly relevant
        url = articles[0].get("link")
        if url:
            content, _ = extract_article_content(url)
            if content:
                return filter_relevant_content(content, keyword)
    
    return f"No relevant articles found for '{keyword}'."

app = Flask(__name__)

@app.route("/")
def home():
    return jsonify({
        "message": "News Scraper API is running",
        "endpoints": {
            "/scrape/<keyword>": "Get latest relevant article for keyword",
            "/health": "Health check"
        }
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "timestamp": datetime.now().isoformat()})

@app.route("/scrape/<keyword>")
def scrape_route(keyword):
    """Enhanced scrape endpoint with better error handling"""
    try:
        if not keyword or len(keyword.strip()) < 2:
            return jsonify({
                "error": "Keyword must be at least 2 characters long"
            }), 400
        
        content = scraper(keyword.strip())
        
        return jsonify({
            "keyword": keyword,
            "content": content,
            "timestamp": datetime.now().isoformat(),
            "status": "success"
        })
    
    except Exception as e:
        return jsonify({
            "error": f"An error occurred: {str(e)}",
            "keyword": keyword,
            "status": "error"
        }), 500

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)

