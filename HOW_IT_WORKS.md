# How It Works: Agentic Newsletter

This document explains the internal architecture and workflow of the Agentic Newsletter system.

## Overview

The system is designed to autonomously crawl the web for AI and tech news, process that information through a multi-agent AI pipeline, and generate a polished markdown newsletter.

## System Architecture

The system consists of four primary components:

1.  **Orchestrator (`main.py`)**: The entry point that handles configuration and decides whether to run once or on a schedule.
2.  **Scheduler (`NewsletterScheduler`)**: Manages the timing of runs and orchestrates the high-level workflow.
3.  **Crawler (`WebCrawler`)**: Fetches live data from the web using Crawl4AI and search tools.
4.  **Agent Pipeline (`NewsletterAgents`)**: A LangGraph-powered workflow that processes articles through specialized AI agents.

## The Workflow

### 1. Data Collection (Crawling)
When a run is triggered:
-   The **Scheduler** calls the **WebCrawler**.
-   The crawler takes a list of **Topics** (from `config.py`) and searches for recent articles.
-   It uses **Crawl4AI** to extract clean content from web pages, bypassing noise like ads and navigation.

### 2. Multi-Agent Pipeline (LangGraph)
Once articles are collected, they are passed into a directed acyclic graph (DAG) managed by **LangGraph**. The state is passed sequentially through four agents:

#### A. Researcher Agent
-   **Input**: Raw article data.
-   **Task**: Categorizes articles, identifies the most important stories, and extracts key facts.
-   **Output**: A structured research summary.

#### B. Analyst Agent
-   **Input**: Research summary.
-   **Task**: Analyzes the implications of the news, looks for deeper insights, and connects different stories.
-   **Output**: Key insights and trend analysis.

#### C. Opinion Writer Agent
-   **Input**: Insights from the Analyst.
-   **Task**: Adds an "editorial voice," providing commentary and perspective on why this news matters to the industry.
-   **Output**: Editorial commentary.

#### D. Editor Agent
-   **Input**: All previous outputs (Summary, Insights, Opinion).
-   **Task**: Formats everything into a beautiful, cohesive markdown newsletter with a title, table of contents, and clean sections.
-   **Output**: Final newsletter content.

### 3. Delivery and Storage
-   The final newsletter is saved as a markdown file in the `newsletters/` directory.
-   Logs of the entire process are stored in `logs/` for auditing and troubleshooting.

## Key Technologies
-   **LangChain / LangGraph**: Orchestration of AI agents and state management.
-   **Crawl4AI**: High-performance web crawling and content extraction.
-   **OpenAI GPT-4o**: The "brain" behind the agents.
-   **FastAPI**: Provides a web dashboard and API for manual control.
-   **Docker**: Ensures a consistent environment for all dependencies (especially Chromium).
