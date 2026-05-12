import os
from typing import List
from dotenv import load_dotenv

load_dotenv()

class Config:
    # OpenAI Configuration
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

    # Newsletter Configuration
    NEWSLETTER_TITLE = os.getenv("NEWSLETTER_TITLE", "Daily AI Newsletter")
    
    # Scheduling Configuration
    SCHEDULE_TIMES = os.getenv("SCHEDULE_TIMES", "08:00").split(",")
    TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")
    
    # Crawling Configuration
    MAX_ARTICLES_PER_TOPIC = int(os.getenv("MAX_ARTICLES_PER_TOPIC", "5"))
    CRAWL_TIMEOUT = int(os.getenv("CRAWL_TIMEOUT", "30"))
    
    # LLM Configuration
    DEFAULT_MODEL = os.getenv("DEFAULT_MODEL", "gpt-5-mini")
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

    # Nitter (X/Twitter scraping via RSS)
    NITTER_INSTANCE = os.getenv("NITTER_INSTANCE", "https://nitter.net")
    X_ACCOUNTS = [
        "openai",
        "AnthropicAI",
        "GoogleDeepMind",
        "sama",
        "karpathy",
        "ylecun",
        "huggingface",
        "techcrunch",
        "theverge",
    ]

config = Config()