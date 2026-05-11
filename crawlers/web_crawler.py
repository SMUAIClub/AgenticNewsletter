import asyncio
import httpx
import requests
from typing import List, Dict, Optional
from crawl4ai import AsyncWebCrawler, CrawlerRunConfig, LLMConfig, BrowserConfig, CacheMode
from crawl4ai import LLMExtractionStrategy
import feedparser
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import urllib.parse
import re

from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

class WebCrawler:
    def __init__(self):
        self.timeout = config.CRAWL_TIMEOUT
        self.max_articles = config.MAX_ARTICLES_PER_TOPIC
        
    async def crawl_with_crawl4ai(self, url: str, topic: str) -> List[Dict]:
        """Crawl a single URL using Crawl4AI"""
        try:
            browser_config = BrowserConfig(headless=True)
            
            crawler_config = CrawlerRunConfig(
                cache_mode=CacheMode.BYPASS,
                word_count_threshold=10,
                page_timeout=60000
            )
            
            async with AsyncWebCrawler(config=browser_config) as crawler:
                result = await crawler.arun(url=url, config=crawler_config)
                
                if result.success:
                    # Use HTML parsing instead of LLM extraction
                    if hasattr(result, 'cleaned_html') and result.cleaned_html:
                        articles = self._extract_articles_from_html(result.cleaned_html, url, topic)
                        logger.info(f"Extracted {len(articles)} articles from {url}")
                        return articles[:self.max_articles]
                    elif hasattr(result, 'markdown') and result.markdown:
                        articles = self._extract_articles_from_markdown(result.markdown, url, topic)
                        logger.info(f"Extracted {len(articles)} articles from {url}")
                        return articles[:self.max_articles]
                else:
                    logger.warning(f"Failed to crawl {url}: {getattr(result, 'error_message', 'Unknown error')}")
                    return []
                    
        except Exception as e:
            logger.error(f"Error crawling {url}: {str(e)}")
            # Fallback to simple httpx-based crawling
            return await self._fallback_crawl(url, topic)
    
    async def _fallback_crawl(self, url: str, topic: str) -> List[Dict]:
        """Fallback crawler using httpx when Crawl4AI fails"""
        try:
            logger.info(f"Using fallback crawler for {url}")
            async with httpx.AsyncClient(timeout=15) as client:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = await client.get(url, headers=headers)
                response.raise_for_status()
                
                articles = self._extract_articles_from_html(response.text, url, topic)
                logger.info(f"Fallback crawler extracted {len(articles)} articles from {url}")
                return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"Fallback crawler failed for {url}: {str(e)}")
            return []
    
    def crawl_rss_feeds(self, rss_urls: List[str], topic: str) -> List[Dict]:
        """Crawl RSS feeds in parallel using a thread pool"""
        from concurrent.futures import ThreadPoolExecutor, as_completed

        def fetch_one(rss_url: str) -> List[Dict]:
            try:
                feed = feedparser.parse(rss_url)
                results = []
                for entry in feed.entries[:self.max_articles]:
                    results.append({
                        "title": entry.get("title", ""),
                        "summary": entry.get("summary", ""),
                        "url": entry.get("link", ""),
                        "published_date": entry.get("published", ""),
                        "content": "",
                        "topic": topic
                    })
                return results
            except Exception as e:
                logger.error(f"Error parsing RSS feed {rss_url}: {str(e)}")
                return []

        articles = []
        with ThreadPoolExecutor(max_workers=10) as executor:
            futures = {executor.submit(fetch_one, url): url for url in rss_urls}
            for future in as_completed(futures):
                articles.extend(future.result())
        return articles
    
    def _extract_content_from_url(self, url: str) -> str:
        """Extract content from a single URL using requests and BeautifulSoup"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
            response = requests.get(url, headers=headers, timeout=self.timeout)
            response.raise_for_status()
            
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Get text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            # Return first 1000 characters
            return text[:1000] + "..." if len(text) > 1000 else text
            
        except Exception as e:
            logger.error(f"Error extracting content from {url}: {str(e)}")
            return ""
    
    async def search_news_urls(self, topic: str) -> List[str]:
        """Search for news URLs using search engines"""
        search_urls = []
        search_query = f"{topic} news site:techcrunch.com OR site:theverge.com OR site:venturebeat.com OR site:wired.com"
        
        # DuckDuckGo search (no API key needed)
        duckduckgo_url = f"https://html.duckduckgo.com/html/?q={urllib.parse.quote(search_query)}"
        
        try:
            async with httpx.AsyncClient(timeout=15) as client:
                headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
                response = await client.get(duckduckgo_url, headers=headers)
                
                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    links = soup.find_all('a', href=True)
                    
                    for link in links[:10]:  # First 10 results
                        href = link.get('href')
                        if href and any(domain in href for domain in ['techcrunch.com', 'theverge.com', 'venturebeat.com', 'wired.com']):
                            if href.startswith('http'):
                                search_urls.append(href)
                            
        except Exception as e:
            logger.error(f"Search failed: {str(e)}")
            # Fallback to static URLs if search fails
            search_urls = config.NEWS_SOURCES
        
        # If no search results, use fallback URLs
        if not search_urls:
            search_urls = config.NEWS_SOURCES
            
        return search_urls[:5]  # Limit to 5 URLs
    
    def _build_nitter_rss_urls(self, topic: str) -> List[str]:
        """Build Nitter RSS URLs for configured X accounts and topic search"""
        urls = []
        for account in config.X_ACCOUNTS:
            urls.append(f"{config.NITTER_INSTANCE}/{account}/rss")
        encoded_topic = urllib.parse.quote(topic)
        urls.append(f"{config.NITTER_INSTANCE}/search/rss?q={encoded_topic}&f=tweets")
        return urls

    async def _fetch_nitter(self, topic: str) -> List[Dict]:
        """Run synchronous Nitter RSS fetch in a thread so it doesn't block the event loop"""
        nitter_urls = self._build_nitter_rss_urls(topic)
        logger.info(f"Fetching {len(nitter_urls)} Nitter RSS feeds for {topic}")
        articles = await asyncio.to_thread(self.crawl_rss_feeds, nitter_urls, topic)
        logger.info(f"Got {len(articles)} posts from Nitter for {topic}")
        return articles

    async def _fetch_web(self, topic: str) -> List[Dict]:
        """DuckDuckGo search + Crawl4AI pipeline"""
        search_urls = await self.search_news_urls(topic)
        logger.info(f"Found {len(search_urls)} URLs to crawl for {topic}")
        crawl_results = await asyncio.gather(
            *[self.crawl_with_crawl4ai(url, topic) for url in search_urls],
            return_exceptions=True
        )
        articles = []
        for result in crawl_results:
            if isinstance(result, list):
                articles.extend(result)
            elif isinstance(result, Exception):
                logger.error(f"Crawling task failed: {str(result)}")
        return articles

    async def fetch_live_data(self, topic: str) -> List[Dict]:
        """Main method to fetch live data for a topic using dynamic search"""
        logger.info(f"Fetching live data for topic: {topic}")

        nitter_articles, web_articles = await asyncio.gather(
            self._fetch_nitter(topic),
            self._fetch_web(topic),
            return_exceptions=False
        )

        all_articles = nitter_articles + web_articles
        filtered_articles = self._filter_articles(all_articles, topic)

        logger.info(f"Found {len(filtered_articles)} relevant articles for {topic}")
        return filtered_articles
    
    def _parse_llm_extraction(self, extracted_content: str, source_url: str, topic: str) -> List[Dict]:
        """Parse LLM extracted content into article format"""
        try:
            articles = []
            
            # Convert to string if not already
            content_str = str(extracted_content)
            
            # Try to extract from text directly - most reliable approach
            articles_data = self._extract_from_text(content_str)
            
            for item in articles_data:
                if isinstance(item, dict) and item.get("title"):
                    article = {
                        "title": item.get("title", "").strip(),
                        "summary": item.get("summary", "").strip(),
                        "url": item.get("url", source_url),
                        "published_date": datetime.now().strftime("%Y-%m-%d"),
                        "content": item.get("summary", "").strip(),
                        "topic": topic
                    }
                    articles.append(article)
            
            return articles
            
        except Exception as e:
            logger.error(f"Error parsing LLM extraction: {str(e)}")
            return []
    
    def _extract_from_text(self, text: str) -> List[Dict]:
        """Extract articles from plain text LLM response"""
        articles = []
        
        # Split text into potential article sections
        import re
        
        # Look for numbered lists, bullet points, or clear separators
        sections = re.split(r'\n\s*(?:\d+[.):]|[-*•]|Article|Title)', text)
        
        for section in sections:
            section = section.strip()
            if len(section) < 30:  # Skip very short sections
                continue
                
            lines = [line.strip() for line in section.split('\n') if line.strip()]
            if not lines:
                continue
                
            # Extract title (first meaningful line)
            title = lines[0]
            title = re.sub(r'^[:\-\s]+', '', title).strip()  # Clean prefixes
            
            # Extract summary (remaining lines)
            summary_lines = lines[1:] if len(lines) > 1 else []
            summary = ' '.join(summary_lines)[:400] if summary_lines else title[:200]
            
            # Basic validation - must look like a news title
            if (title and len(title) > 15 and len(title) < 200 and 
                not title.lower().startswith(('http', 'www', 'click', 'read more'))):
                articles.append({
                    "title": title,
                    "summary": summary
                })
                
                if len(articles) >= 10:  # Limit to prevent too many
                    break
        
        return articles
    
    def _extract_articles_from_markdown(self, markdown_content: str, source_url: str, topic: str) -> List[Dict]:
        """Extract articles from markdown content"""
        try:
            articles = []
            lines = markdown_content.split('\n')
            
            current_title = None
            current_content = []
            
            for line in lines:
                line = line.strip()
                if not line:
                    continue
                    
                # Look for headers (titles)
                if line.startswith('#'):
                    # Save previous article if exists
                    if current_title and len(current_title) > 15:
                        summary = ' '.join(current_content)[:300]
                        articles.append({
                            "title": current_title,
                            "summary": summary,
                            "url": source_url,
                            "published_date": datetime.now().strftime("%Y-%m-%d"),
                            "content": summary,
                            "topic": topic
                        })
                        
                        if len(articles) >= self.max_articles:
                            break
                    
                    # Start new article
                    current_title = line.lstrip('#').strip()
                    current_content = []
                    
                elif current_title:
                    # Add to current article content
                    if not line.startswith('[') and not line.startswith('http'):
                        current_content.append(line)
            
            # Don't forget the last article
            if current_title and len(current_title) > 15:
                summary = ' '.join(current_content)[:300]
                articles.append({
                    "title": current_title,
                    "summary": summary,
                    "url": source_url,
                    "published_date": datetime.now().strftime("%Y-%m-%d"),
                    "content": summary,
                    "topic": topic
                })
            
            return articles[:self.max_articles]
            
        except Exception as e:
            logger.error(f"Error extracting articles from markdown: {str(e)}")
            return []
    
    def _extract_articles_from_html(self, html_content: str, source_url: str, topic: str) -> List[Dict]:
        """Extract articles from HTML content using BeautifulSoup"""
        try:
            soup = BeautifulSoup(html_content, 'html.parser')
            articles = []
            
            # Common selectors for article elements
            article_selectors = [
                'article',
                '.post',
                '.article',
                '.story',
                '.entry',
                '[data-testid="post"]',
                '.c-entry-box--compact',
                '.post-item',
                '.article-item',
                '.news-item',
                'h2',
                'h3'
            ]
            
            for selector in article_selectors:
                elements = soup.select(selector)[:self.max_articles * 2]  # Get more to filter later
                
                for element in elements:
                    title_elem = element.find(['h1', 'h2', 'h3', 'h4']) or element.find(class_=lambda x: x and 'title' in x.lower() if x else False)
                    link_elem = element.find('a', href=True) or element.find(class_=lambda x: x and 'link' in x.lower() if x else False)
                    
                    if title_elem and title_elem.get_text(strip=True):
                        title = title_elem.get_text(strip=True)
                        
                        # Get article URL
                        article_url = source_url
                        if link_elem and link_elem.get('href'):
                            href = link_elem.get('href')
                            if href.startswith('http'):
                                article_url = href
                            elif href.startswith('/'):
                                from urllib.parse import urljoin
                                article_url = urljoin(source_url, href)
                        
                        # Get summary/content
                        summary = ""
                        content_elem = element.find(['p', 'div'], class_=lambda x: x and any(word in x.lower() for word in ['summary', 'excerpt', 'description']) if x else False)
                        if content_elem:
                            summary = content_elem.get_text(strip=True)[:300]
                        else:
                            # Fallback: get first paragraph
                            p_elem = element.find('p')
                            if p_elem:
                                summary = p_elem.get_text(strip=True)[:300]
                        
                        article = {
                            "title": title,
                            "summary": summary,
                            "url": article_url,
                            "published_date": datetime.now().strftime("%Y-%m-%d"),
                            "content": summary,
                            "topic": topic
                        }
                        articles.append(article)
                        
                        if len(articles) >= self.max_articles:
                            break
                
                if articles:
                    break  # Found articles with this selector
            
            return articles
            
        except Exception as e:
            logger.error(f"Error extracting articles from HTML: {str(e)}")
            return []
    
    def _filter_articles(self, articles: List[Dict], topic: str) -> List[Dict]:
        """Filter articles by relevance and recency"""
        filtered = []
        topic_keywords = topic.lower().split()
        
        for article in articles:
            # Check if article is relevant to topic
            title_lower = article.get("title", "").lower()
            summary_lower = article.get("summary", "").lower()
            
            relevance_score = 0
            for keyword in topic_keywords:
                if keyword in title_lower:
                    relevance_score += 2
                if keyword in summary_lower:
                    relevance_score += 1
            
            # If no specific relevance found, still include if it's a tech/AI article
            if relevance_score == 0:
                tech_keywords = ['ai', 'artificial', 'intelligence', 'tech', 'technology', 'startup', 'google', 'openai', 'machine', 'learning', 'data', 'algorithm', 'neural', 'deep']
                for keyword in tech_keywords:
                    if keyword in title_lower or keyword in summary_lower:
                        relevance_score = 1
                        break
            
            if relevance_score > 0:
                article["relevance_score"] = relevance_score
                article["topic"] = topic
                filtered.append(article)
        
        # Sort by relevance score and return top articles
        filtered.sort(key=lambda x: x.get("relevance_score", 0), reverse=True)
        return filtered[:self.max_articles]