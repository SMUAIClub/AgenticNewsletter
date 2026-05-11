from typing import Dict, Any

from agents.llm_client import OpenAIClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


def analysis_agent(state: Dict[str, Any], llm_client: OpenAIClient) -> Dict[str, Any]:
    """Provides deep insights and implications from the research summary."""
    logger.info("Analysis agent processing research...")

    research_summary = state.get("research_summary", "")
    if not research_summary:
        logger.warning("No research summary provided to analysis agent")
        return state

    system_message = """You are an analysis agent for an AI newsletter. Your job is to:
1. Provide deep insights into the implications of the news
2. Connect dots between different stories
3. Analyze market impact and future predictions
4. Identify opportunities and risks

Focus on providing valuable analysis that goes beyond surface-level reporting."""

    prompt = f"""Based on this research summary, provide deep analytical insights:

{research_summary}

Please provide:
1. **Strategic Implications**: What do these developments mean for the AI industry?
2. **Market Impact**: How might these affect businesses and investors?
3. **Technology Trends**: What technical directions are emerging?
4. **Future Predictions**: What might happen next based on these developments?
5. **Opportunities & Risks**: What should readers watch out for?

Provide thoughtful, well-reasoned analysis with specific examples."""

    state["key_insights"] = llm_client.generate_completion(
        prompt=prompt,
        system_message=system_message,
        temperature=0.4,
    )
    logger.info("Analysis agent completed insights")
    return state
