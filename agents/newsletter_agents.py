from typing import List, Dict, Any, TypedDict

from langgraph.graph import StateGraph, END

from agents.llm_client import OpenAIClient
from agents.workers import research_agent, analysis_agent, opinion_agent, editor_agent
from utils.logger import setup_logger

logger = setup_logger(__name__)


class NewsletterState(TypedDict):
    raw_articles: List[Dict]
    research_summary: str
    key_insights: str
    opinion_analysis: str
    final_newsletter: str


class NewsletterAgents:
    def __init__(self):
        self.llm_client = OpenAIClient()
        self.graph = self._create_agent_graph()

    def _create_agent_graph(self) -> StateGraph:
        workflow = StateGraph(NewsletterState)

        workflow.add_node("researcher", lambda s: research_agent(s, self.llm_client))
        workflow.add_node("analyst", lambda s: analysis_agent(s, self.llm_client))
        workflow.add_node("opinion_writer", lambda s: opinion_agent(s, self.llm_client))
        workflow.add_node("editor", lambda s: editor_agent(s, self.llm_client))

        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "opinion_writer")
        workflow.add_edge("opinion_writer", "editor")
        workflow.add_edge("editor", END)

        workflow.set_entry_point("researcher")

        return workflow.compile()

    def process_articles(self, articles: List[Dict]) -> Dict[str, Any]:
        logger.info(f"Processing {len(articles)} articles through agent workflow")

        initial_state: NewsletterState = {
            "raw_articles": articles,
            "research_summary": "",
            "key_insights": "",
            "opinion_analysis": "",
            "final_newsletter": "",
        }

        try:
            final_state = self.graph.invoke(initial_state)
            logger.info("Agent workflow completed successfully")
            return final_state
        except Exception as e:
            logger.error(f"Error in agent workflow: {str(e)}")
            return initial_state
