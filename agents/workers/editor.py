from typing import Dict, Any, List

from agents.llm_client import OpenAIClient
from utils.logger import setup_logger

logger = setup_logger(__name__)


def _build_sources_section(articles: List[Dict]) -> str:
    """Build a markdown sources appendix from raw articles."""
    if not articles:
        return ""

    seen_urls = set()
    lines = ["\n\n---\n\n## All Sources Found\n"]
    for article in articles:
        url = article.get("url", "")
        title = article.get("title", "").strip()
        summary = article.get("summary", "").strip()
        if not title or url in seen_urls:
            continue
        seen_urls.add(url)
        one_liner = summary[:120].rstrip() + ("…" if len(summary) > 120 else "")
        if url:
            lines.append(f"- [{title}]({url}) — {one_liner}")
        else:
            lines.append(f"- **{title}** — {one_liner}")

    return "\n".join(lines)


def editor_agent(state: Dict[str, Any], llm_client: OpenAIClient) -> Dict[str, Any]:
    """Compiles all content into a final formatted newsletter."""
    logger.info("Editor agent compiling final newsletter...")

    research_summary = state.get("research_summary", "")
    key_insights = state.get("key_insights", "")
    opinion_analysis = state.get("opinion_analysis", "")
    raw_articles: List[Dict] = state.get("raw_articles", [])

    system_message = """You are the editor of an AI newsletter. Your job is to:
1. Compile all content into a cohesive, well-formatted newsletter
2. Ensure proper flow and readability
3. Add engaging headlines and section breaks
4. Include a compelling introduction and conclusion
5. Format for email delivery

Create a professional, engaging newsletter that readers will want to read and share."""

    prompt = f"""Compile this content into a final newsletter format:

**Research Summary:**
{research_summary}

**Key Insights:**
{key_insights}

**Opinion & Commentary:**
{opinion_analysis}

Create a complete newsletter with:
1. **Compelling Subject Line Suggestion**
2. **Engaging Introduction** (hook the reader)
3. **Well-organized Sections** with clear headers
4. **Smooth Transitions** between sections
5. **Strong Conclusion** with key takeaways
6. **Call to Action** (encourage engagement)

IMPORTANT: Every story or article mentioned must include a clickable markdown link to its source, e.g. [Read more](https://...) or the title as a hyperlink. Do not drop any URLs from the research summary.
Format in Markdown with proper spacing. Make it professional yet engaging."""

    newsletter = llm_client.generate_completion(
        prompt=prompt,
        system_message=system_message,
        temperature=0.4,
    )

    newsletter += _build_sources_section(raw_articles)

    state["final_newsletter"] = newsletter
    logger.info("Editor agent completed final newsletter")
    return state
