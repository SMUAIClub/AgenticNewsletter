import schedule
import time
import asyncio
import logging
from typing import List
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from crawlers.web_crawler import WebCrawler
from agents.newsletter_agents import NewsletterAgents
from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)


def _get_run_logger(source: str) -> logging.Logger:
    """Attach a source-specific file handler to the root logger so all modules log to it."""
    Path("logs").mkdir(exist_ok=True)
    date = datetime.now().strftime("%Y%m%d")
    filename = f"logs/{source}_{date}.log"
    formatter = logging.Formatter("%(asctime)s - %(name)s - %(levelname)s - %(message)s")

    root = logging.getLogger()
    root.setLevel(logging.INFO)
    # Only add the handler once per file
    if not any(
        isinstance(h, logging.FileHandler) and h.baseFilename.endswith(f"{source}_{date}.log")
        for h in root.handlers
    ):
        fh = logging.FileHandler(filename)
        fh.setFormatter(formatter)
        fh.setLevel(logging.INFO)
        root.addHandler(fh)

    return logging.getLogger(f"newsletter.{source}")


class NewsletterScheduler:
    def __init__(self):
        self.crawler = WebCrawler()
        self.agents = NewsletterAgents()
        self.is_running = False

    async def newsletter_run(self, source: str = "manual"):
        """Main newsletter generation workflow"""
        run_logger = _get_run_logger(source)
        run_logger.info("=" * 50)
        run_logger.info(f"Starting newsletter generation [{source}]")
        run_logger.info("=" * 50)

        try:
            # Step 1: Crawl all topics in parallel
            run_logger.info("Step 1: Crawling all topics in parallel...")
            results = await asyncio.gather(
                *[self.crawler.fetch_live_data(topic) for topic in config.TOPICS],
                return_exceptions=True
            )
            all_articles = []
            for topic, result in zip(config.TOPICS, results):
                if isinstance(result, Exception):
                    run_logger.error(f"Failed to crawl topic '{topic}': {result}")
                else:
                    all_articles.extend(result)

            if not all_articles:
                run_logger.warning("No articles found. Skipping newsletter generation.")
                return

            run_logger.info(f"Total articles collected: {len(all_articles)}")

            # Step 2: Process articles through agent workflow
            run_logger.info("Step 2: Processing articles through AI agents...")
            agent_results = self.agents.process_articles(all_articles)

            final_newsletter = agent_results.get("final_newsletter", "")
            run_logger.info(f"Generated newsletter content length: {len(final_newsletter)}")

            if not final_newsletter:
                run_logger.error("Failed to generate newsletter content")
                return

            # Save full newsletter to file
            output_dir = Path("newsletters")
            output_dir.mkdir(exist_ok=True)
            filename = output_dir / f"newsletter_{source}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
            filename.write_text(final_newsletter)
            run_logger.info(f"Newsletter saved to {filename}")
            run_logger.info("Newsletter generation completed successfully!")

        except Exception as e:
            run_logger.error(f"Error in newsletter generation: {str(e)}")
            raise

    @staticmethod
    def _to_local_time(time_str: str) -> str:
        """Convert HH:MM in the configured timezone to local system time."""
        tz = ZoneInfo(config.TIMEZONE)
        now = datetime.now()
        hour, minute = map(int, time_str.split(":"))
        dt_in_tz = datetime(now.year, now.month, now.day, hour, minute, tzinfo=tz)
        return dt_in_tz.astimezone().strftime("%H:%M")

    def schedule_newsletter(self):
        """Schedule newsletter generation at configured times"""
        logger.info(f"Setting up newsletter schedule (timezone: {config.TIMEZONE})...")
        for time_str in config.SCHEDULE_TIMES:
            time_str = time_str.strip()
            local_time = self._to_local_time(time_str)
            logger.info(f"Scheduling newsletter for {time_str} {config.TIMEZONE} → {local_time} local")
            schedule.every().day.at(local_time).do(self._run_async_newsletter)
        logger.info(f"Newsletter scheduled for: {', '.join(config.SCHEDULE_TIMES)} ({config.TIMEZONE})")

    def _run_async_newsletter(self):
        """Wrapper to run async newsletter function from scheduler"""
        try:
            asyncio.run(self.newsletter_run(source="scheduled"))
        except Exception as e:
            logger.error(f"Error running scheduled newsletter: {str(e)}")

    def run_once(self):
        """Run newsletter generation once (for testing)"""
        logger.info("Running newsletter generation once...")
        asyncio.run(self.newsletter_run(source="manual"))

    def start_scheduler(self):
        """Start the scheduler loop"""
        self.schedule_newsletter()
        self.is_running = True
        logger.info("Newsletter scheduler started. Press Ctrl+C to stop.")
        logger.info(f"Next scheduled runs: {schedule.jobs}")
        try:
            while self.is_running:
                schedule.run_pending()
                time.sleep(60)
        except KeyboardInterrupt:
            logger.info("Scheduler stopped by user")
            self.is_running = False
        except Exception as e:
            logger.error(f"Scheduler error: {str(e)}")
            self.is_running = False

    def stop_scheduler(self):
        """Stop the scheduler"""
        self.is_running = False
        schedule.clear()
        logger.info("Newsletter scheduler stopped")

    def get_schedule_info(self) -> List[str]:
        job_info = []
        for job in schedule.jobs:
            job_info.append(f"Next run: {job.next_run}")
        return job_info
