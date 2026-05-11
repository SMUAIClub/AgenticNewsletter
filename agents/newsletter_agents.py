from typing import List, Dict, Any
from langchain.schema import BaseMessage, HumanMessage, SystemMessage
from langgraph.graph import StateGraph, END
import json

from agents.llm_client import OpenAIClient
from utils.logger import setup_logger

logger = setup_logger(__name__)

class NewsletterAgents:
    def __init__(self):
        self.llm_client = OpenAIClient()
        self.graph = self._create_agent_graph()
    
    def _create_agent_graph(self) -> StateGraph:
        """Create the multi-agent workflow graph using LangGraph"""
        
        # Define the state structure as a dictionary
        from typing import TypedDict
        
        class NewsletterState(TypedDict):
            raw_articles: List[Dict]
            research_summary: str
            key_insights: str
            opinion_analysis: str
            final_newsletter: str
        
        # Create workflow graph
        workflow = StateGraph(NewsletterState)
        
        # Add nodes (agents)
        workflow.add_node("researcher", self._research_agent)
        workflow.add_node("analyst", self._analysis_agent)
        workflow.add_node("opinion_writer", self._opinion_agent)
        workflow.add_node("editor", self._editor_agent)
        
        # Define the workflow edges
        workflow.add_edge("researcher", "analyst")
        workflow.add_edge("analyst", "opinion_writer")
        workflow.add_edge("opinion_writer", "editor")
        workflow.add_edge("editor", END)
        
        # Set entry point
        workflow.set_entry_point("researcher")
        
        return workflow.compile()
    
    def _research_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Research agent - summarizes and categorizes articles"""
        logger.info("Research agent processing articles...")
        
        articles = state.get("raw_articles", [])
        if not articles:
            logger.warning("No articles provided to research agent")
            return state
        
        # Create research prompt
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
        
        research_summary = self.llm_client.generate_completion(
            prompt=prompt,
            system_message=system_message,
            temperature=0.3
        )
        
        state["research_summary"] = research_summary
        logger.info("Research agent completed analysis")
        return state
    
    def _analysis_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Analysis agent - provides deep insights and implications"""
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
        
        key_insights = self.llm_client.generate_completion(
            prompt=prompt,
            system_message=system_message,
            temperature=0.4
        )
        
        state["key_insights"] = key_insights
        logger.info("Analysis agent completed insights")
        return state
    
    def _opinion_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Opinion agent - provides editorial perspective and commentary"""
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
        
        opinion_analysis = self.llm_client.generate_completion(
            prompt=prompt,
            system_message=system_message,
            temperature=0.6
        )
        
        state["opinion_analysis"] = opinion_analysis
        logger.info("Opinion agent completed commentary")
        return state
    
    def _editor_agent(self, state: Dict[str, Any]) -> Dict[str, Any]:
        """Editor agent - compiles final newsletter with proper formatting"""
        logger.info("Editor agent compiling final newsletter...")
        
        research_summary = state.get("research_summary", "")
        key_insights = state.get("key_insights", "")
        opinion_analysis = state.get("opinion_analysis", "")
        
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
        
        final_newsletter = self.llm_client.generate_completion(
            prompt=prompt,
            system_message=system_message,
            temperature=0.4
        )
        
        state["final_newsletter"] = final_newsletter
        logger.info("Editor agent completed final newsletter")
        return state
    
    def process_articles(self, articles: List[Dict]) -> Dict[str, Any]:
        """Main method to process articles through the agent workflow"""
        logger.info(f"Processing {len(articles)} articles through agent workflow")
        
        # Initialize state
        initial_state = {
            "raw_articles": articles,
            "research_summary": "",
            "key_insights": "",
            "opinion_analysis": "",
            "final_newsletter": ""
        }
        
        try:
            # Run the workflow
            final_state = self.graph.invoke(initial_state)
            
            logger.info("Agent workflow completed successfully")
            return final_state
            
        except Exception as e:
            logger.error(f"Error in agent workflow: {str(e)}")
            return initial_state