import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenRouter Configuration
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    OPENROUTER_BASE_URL = os.getenv("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1")
    
    # Gmail Configuration
    GMAIL_CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")
    GMAIL_TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")
    
    # Newsletter Configuration
    SENDER_EMAIL = os.getenv("SENDER_EMAIL")
    RECIPIENT_EMAILS = os.getenv("RECIPIENT_EMAILS", "").split(",")
    NEWSLETTER_TITLE = os.getenv("NEWSLETTER_TITLE", "Daily AI Newsletter")
    
    # Scheduling Configuration
    SCHEDULE_TIMES = os.getenv("SCHEDULE_TIMES", "08:00,18:00").split(",")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
    
    # Crawling Configuration
    MAX_ARTICLES_PER_TOPIC = int(os.getenv("MAX_ARTICLES_PER_TOPIC", "5"))
    CRAWL_TIMEOUT = int(os.getenv("CRAWL_TIMEOUT", "30"))
    
    # LLM Configuration
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-4-turbo-preview")
    TEMPERATURE = float(os.getenv("TEMPERATURE", "0.7"))
    MAX_TOKENS = int(os.getenv("MAX_TOKENS", "2000"))
    
    # Topics to crawl
    TOPICS = [
        "AI news",
        "Machine Learning breakthroughs",
        "Tech startups",
        "OpenAI updates",
        "Google AI developments",
        "Tech industry trends"
    ]
    
    # News sources
    NEWS_SOURCES = [
        "https://techcrunch.com/category/artificial-intelligence/",
        "https://www.theverge.com/ai-artificial-intelligence",
        "https://venturebeat.com/ai/",
        "https://www.wired.com/tag/artificial-intelligence/",
        "https://www.artificialintelligence-news.com/"
    ]

config = Config()