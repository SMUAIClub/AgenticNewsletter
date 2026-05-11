from typing import Dict, Any, List

from agents.llm_client import OpenAIClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


def research_agent(state: Dict[str, Any], llm_client: OpenAIClient) -> Dict[str, Any]:
    """Summarizes and categorizes raw articles."""
    logger.info("Research agent processing articles...")

    articles: List[Dict] = state.get("raw_articles", [])
    if not articles:
        logger.warning("No articles provided to research agent")
        return state

    articles_text = ""
    for i, article in enumerate(articles, 1):
        articles_text += f"\n{i}. **{article.get('title', 'No title')}**\n"
        articles_text += f"   Topic: {article.get('topic', 'Unknown')}\n"
        articles_text += f"   Summary: {article.get('summary', 'No summary')}\n"
        articles_text += f"   URL: {article.get('url', 'No URL')}\n"

    system_message = """You are a research agent for an AI newsletter. Your job is to:
1. Analyze and categorize the provided articles
2. Identify the most important stories
3. Create a structured research summary
4. Highlight emerging trends and patterns

Focus on accuracy, relevance, and providing clear categorization."""

    prompt = f"""Please analyze these articles and create a comprehensive research summary:

{articles_text}

Provide a structured summary that includes:
1. **Key Categories**: Group articles by themes/topics
2. **Most Important Stories**: Highlight the top 3-5 most significant articles — include the article URL for each as a markdown link
3. **Emerging Trends**: Identify patterns across articles
4. **Quick Facts**: Extract key statistics, dates, and figures

IMPORTANT: For every article you mention, include its URL as a markdown hyperlink, e.g. [Article Title](https://...).
Format your response in clear sections with headers."""

    state["research_summary"] = llm_client.generate_completion(
        prompt=prompt,
        system_message=system_message,
        temperature=0.3,
    )
    logger.info("Research agent completed analysis")
    return state
