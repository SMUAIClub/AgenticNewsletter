#!/usr/bin/env python3
"""
24/7 AI Newsletter Agent
Main entry point for the newsletter generation system
"""

import argparse
import asyncio
import sys
from datetime import datetime

from scheduler.newsletter_scheduler import NewsletterScheduler
from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

def print_banner():
    """Print application banner"""
    banner = """
    ╔══════════════════════════════════════════════════════════════╗
    ║                    24/7 AI Newsletter Agent                  ║
    ║                                                              ║
    ║  Automated AI-powered newsletter generation                  ║
    ║  Built with Crawl4AI, LangGraph & OpenAI API                 ║
    ╚══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def validate_config():
    """Validate configuration before starting"""
    if not config.OPENAI_API_KEY:
        logger.error("OpenAI API key not configured. Please check your .env file.")
        return False
    return True

def main():
    """Main application entry point"""
    parser = argparse.ArgumentParser(description="24/7 AI Newsletter Agent")
    parser.add_argument(
        "--mode", 
        choices=["schedule", "once", "test"],
        default="schedule",
        help="Run mode: schedule (continuous), once (single run), or test (dry run)"
    )
    parser.add_argument(
        "--config-check",
        action="store_true",
        help="Check configuration and exit"
    )
    
    args = parser.parse_args()
    
    print_banner()
    logger.info(f"Starting AI Newsletter Agent in {args.mode} mode")
    logger.info(f"Configuration: {len(config.TOPICS)} topics")
    
    # Validate configuration
    if not validate_config():
        sys.exit(1)
    
    if args.config_check:
        logger.info("Configuration check passed!")
        logger.info(f"Topics: {', '.join(config.TOPICS)}")
        logger.info(f"Schedule times: {', '.join(config.SCHEDULE_TIMES)}")
        logger.info(f"Recipients: {len(config.RECIPIENT_EMAILS)} configured")
        return
    
    # Initialize scheduler
    scheduler = NewsletterScheduler()
    
    try:
        if args.mode == "once":
            logger.info("Running newsletter generation once...")
            scheduler.run_once()
            
        elif args.mode == "test":
            logger.info("Running in test mode (dry run)...")
            # TODO: Implement test mode with mock data
            logger.info("Test mode not yet implemented")
            
        elif args.mode == "schedule":
            logger.info("Starting scheduled newsletter service...")
            scheduler.start_scheduler()
            
    except KeyboardInterrupt:
        logger.info("Application stopped by user")
    except Exception as e:
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        if hasattr(scheduler, 'stop_scheduler'):
            scheduler.stop_scheduler()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()