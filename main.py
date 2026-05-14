#!/usr/bin/env python3
"""
24/7 AI Newsletter Agent
Main entry point for the newsletter generation system.
This script orchestrates the entire process from configuration validation to 
triggering the newsletter generation either once or on a schedule.
"""

import argparse
import asyncio
import sys
from datetime import datetime

# Import core components
from scheduler.newsletter_scheduler import NewsletterScheduler
from utils.logger import setup_logger
from config import config

# Initialize the main logger for the application
logger = setup_logger(__name__)

def print_banner():
    """
    Prints a decorative banner to the console when the application starts.
    This helps in identifying the service in terminal logs.
    """
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
    """
    Validates essential configuration settings before the application proceeds.
    Currently checks for the presence of the OpenAI API key.
    
    Returns:
        bool: True if configuration is valid, False otherwise.
    """
    if not config.OPENAI_API_KEY:
        logger.error("OpenAI API key not configured. Please check your .env file.")
        return False
    return True

def main():
    """
    Main application entry point.
    1. Parses command-line arguments to determine the run mode.
    2. Validates the environment and configuration.
    3. Initializes the NewsletterScheduler.
    4. Executes the requested mode (once, schedule, or config-check).
    """
    # Define and parse command-line arguments
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
    
    # Display the startup banner
    print_banner()
    logger.info(f"Starting AI Newsletter Agent in {args.mode} mode")
    logger.info(f"Configuration: {len(config.TOPICS)} topics")
    
    # Perform initial configuration validation
    if not validate_config():
        sys.exit(1)
    
    # Handle the --config-check flag
    if args.config_check:
        logger.info("Configuration check passed!")
        logger.info(f"Topics: {', '.join(config.TOPICS)}")
        logger.info(f"Schedule times: {', '.join(config.SCHEDULE_TIMES)}")
        logger.info(f"Recipients: {len(config.RECIPIENT_EMAILS)} configured")
        return
    
    # Initialize the scheduler which handles the workflow execution
    scheduler = NewsletterScheduler()
    
    try:
        if args.mode == "once":
            # Run the generation process immediately and exit
            logger.info("Running newsletter generation once...")
            scheduler.run_once()
            
        elif args.mode == "test":
            # Reserved for future dry-run functionality
            logger.info("Running in test mode (dry run)...")
            # TODO: Implement test mode with mock data
            logger.info("Test mode not yet implemented")
            
        elif args.mode == "schedule":
            # Start the background scheduler to run at configured times
            logger.info("Starting scheduled newsletter service...")
            scheduler.start_scheduler()
            
    except KeyboardInterrupt:
        # Graceful shutdown on manual interruption
        logger.info("Application stopped by user")
    except Exception as e:
        # Log any unexpected errors that crash the main loop
        logger.error(f"Application error: {str(e)}")
        sys.exit(1)
    finally:
        # Ensure the scheduler is cleaned up properly
        if hasattr(scheduler, 'stop_scheduler'):
            scheduler.stop_scheduler()
        logger.info("Application shutdown complete")

if __name__ == "__main__":
    main()