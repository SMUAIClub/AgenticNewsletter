from typing import Dict, Any

from agents.llm_client import OpenAIClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


def opinion_agent(state: Dict[str, Any], llm_client: OpenAIClient) -> Dict[str, Any]:
    """Provides editorial perspective and commentary."""
    logger.info("Opinion agent creating commentary...")

    research_summary = state.get("research_summary", "")
    key_insights = state.get("key_insights", "")

    if not research_summary or not key_insights:
        logger.warning("Insufficient data provided to opinion agent")
        return state

    system_message = """You are an opinion writer for an AI newsletter. Your job is to:
1. Provide thoughtful editorial commentary
2. Offer balanced perspectives on controversial topics
3. Share informed opinions on industry developments
4. Engage readers with compelling viewpoints

Write in an engaging, authoritative tone while remaining balanced and factual."""

    prompt = f"""Based on this research and analysis, provide editorial commentary:

**Research Summary:**
{research_summary}

**Key Insights:**
{key_insights}

Please provide:
1. **Editorial Perspective**: Your informed take on the most important developments
2. **Controversial Takes**: Balanced discussion of debated topics
3. **Industry Commentary**: Opinions on where the AI industry is heading
4. **Reader Engagement**: Thought-provoking questions or calls to action

Write in an engaging, conversational tone that provides value to AI professionals and enthusiasts."""

    state["opinion_analysis"] = llm_client.generate_completion(
        prompt=prompt,
        system_message=system_message,
        temperature=0.6,
    )
    logger.info("Opinion agent completed commentary")
    return state
