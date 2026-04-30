"""
FastAPI server for newsletter management and monitoring
"""

from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.responses import HTMLResponse
from pydantic import BaseModel
from typing import List, Dict, Optional
import asyncio
from datetime import datetime
import json

from scheduler.newsletter_scheduler import NewsletterScheduler
from utils.logger import setup_logger
from config import config

logger = setup_logger(__name__)

app = FastAPI(
    title="AI Newsletter Agent API",
    description="API for managing and monitoring the 24/7 AI Newsletter Agent",
    version="1.0.0"
)

# Global scheduler instance
scheduler = NewsletterScheduler()

# Pydantic models
class NewsletterRequest(BaseModel):
    topics: Optional[List[str]] = None
    recipients: Optional[List[str]] = None

class ConfigUpdate(BaseModel):
    schedule_times: Optional[List[str]] = None
    topics: Optional[List[str]] = None
    max_articles_per_topic: Optional[int] = None

class NewsletterResponse(BaseModel):
    success: bool
    message: str
    newsletter_id: Optional[str] = None

# In-memory storage for demo (use database in production)
newsletter_history = []
system_status = {
    "last_run": None,
    "next_scheduled": None,
    "total_sent": 0,
    "status": "idle"
}

@app.get("/", response_class=HTMLResponse)
async def root():
    """Dashboard homepage"""
    html_content = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>AI Newsletter Agent Dashboard</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 40px; }}
            .header {{ background: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .status {{ margin: 20px 0; padding: 15px; background: #e8f5e9; border-radius: 5px; }}
            .button {{ background: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; margin: 5px; }}
            .config {{ background: #fff3cd; padding: 15px; border-radius: 5px; margin: 20px 0; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>🤖 AI Newsletter Agent Dashboard</h1>
            <p>Automated AI-powered newsletter generation and delivery system</p>
        </div>
        
        <div class="status">
            <h2>System Status</h2>
            <p><strong>Status:</strong> {system_status['status']}</p>
            <p><strong>Last Run:</strong> {system_status['last_run'] or 'Never'}</p>
            <p><strong>Total Sent:</strong> {system_status['total_sent']}</p>
        </div>
        
        <div class="config">
            <h2>Configuration</h2>
            <p><strong>Topics:</strong> {len(config.TOPICS)} configured</p>
            <p><strong>Schedule:</strong> {', '.join(config.SCHEDULE_TIMES)}</p>
            <p><strong>Recipients:</strong> {len(config.RECIPIENT_EMAILS)} configured</p>
        </div>
        
        <div>
            <h2>Actions</h2>
            <a href="/generate" class="button">Generate Newsletter Now</a>
            <a href="/status" class="button">View Status</a>
            <a href="/history" class="button">View History</a>
            <a href="/docs" class="button">API Documentation</a>
        </div>
    </body>
    </html>
    """
    return html_content

@app.get("/status")
async def get_status():
    """Get system status"""
    schedule_info = scheduler.get_schedule_info()
    
    return {
        "status": system_status["status"],
        "last_run": system_status["last_run"],
        "next_scheduled": schedule_info[0] if schedule_info else None,
        "total_newsletters_sent": system_status["total_sent"],
        "configuration": {
            "topics": config.TOPICS,
            "schedule_times": config.SCHEDULE_TIMES,
            "recipients_count": len(config.RECIPIENT_EMAILS),
            "max_articles_per_topic": config.MAX_ARTICLES_PER_TOPIC
        }
    }

@app.post("/generate", response_model=NewsletterResponse)
async def generate_newsletter(
    background_tasks: BackgroundTasks,
    request: NewsletterRequest = None
):
    """Generate newsletter immediately"""
    try:
        newsletter_id = f"newsletter_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Update system status
        system_status["status"] = "generating"
        
        # Run newsletter generation in background
        background_tasks.add_task(run_newsletter_generation, newsletter_id)
        
        return NewsletterResponse(
            success=True,
            message="Newsletter generation started",
            newsletter_id=newsletter_id
        )
        
    except Exception as e:
        logger.error(f"Error starting newsletter generation: {str(e)}")
        system_status["status"] = "error"
        raise HTTPException(status_code=500, detail=str(e))

async def run_newsletter_generation(newsletter_id: str):
    """Background task to run newsletter generation"""
    try:
        logger.info(f"Starting background newsletter generation: {newsletter_id}")
        
        # Run the newsletter generation
        await scheduler.newsletter_run()
        
        # Update status and history
        system_status["status"] = "idle"
        system_status["last_run"] = datetime.now().isoformat()
        system_status["total_sent"] += 1
        
        newsletter_history.append({
            "id": newsletter_id,
            "timestamp": datetime.now().isoformat(),
            "status": "completed",
            "recipients": len(config.RECIPIENT_EMAILS)
        })
        
        logger.info(f"Newsletter generation completed: {newsletter_id}")
        
    except Exception as e:
        logger.error(f"Error in background newsletter generation: {str(e)}")
        system_status["status"] = "error"
        
        newsletter_history.append({
            "id": newsletter_id,
            "timestamp": datetime.now().isoformat(),
            "status": "failed",
            "error": str(e)
        })

@app.get("/history")
async def get_history():
    """Get newsletter generation history"""
    return {
        "history": newsletter_history[-10:],  # Last 10 entries
        "total_count": len(newsletter_history)
    }

@app.post("/schedule/start")
async def start_scheduler():
    """Start the newsletter scheduler"""
    try:
        if system_status["status"] == "scheduled":
            return {"message": "Scheduler is already running"}
        
        # Start scheduler in background
        asyncio.create_task(run_scheduler())
        system_status["status"] = "scheduled"
        
        return {"message": "Newsletter scheduler started"}
        
    except Exception as e:
        logger.error(f"Error starting scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/schedule/stop")
async def stop_scheduler():
    """Stop the newsletter scheduler"""
    try:
        scheduler.stop_scheduler()
        system_status["status"] = "idle"
        return {"message": "Newsletter scheduler stopped"}
        
    except Exception as e:
        logger.error(f"Error stopping scheduler: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

async def run_scheduler():
    """Background task to run the scheduler"""
    try:
        scheduler.start_scheduler()
    except Exception as e:
        logger.error(f"Scheduler error: {str(e)}")
        system_status["status"] = "error"

@app.get("/config")
async def get_config():
    """Get current configuration"""
    return {
        "topics": config.TOPICS,
        "schedule_times": config.SCHEDULE_TIMES,
        "max_articles_per_topic": config.MAX_ARTICLES_PER_TOPIC,
        "recipients_count": len(config.RECIPIENT_EMAILS),
        "newsletter_title": config.NEWSLETTER_TITLE
    }

@app.post("/config")
async def update_config(config_update: ConfigUpdate):
    """Update configuration (runtime only, not persistent)"""
    try:
        updated_fields = []
        
        if config_update.schedule_times:
            config.SCHEDULE_TIMES = config_update.schedule_times
            updated_fields.append("schedule_times")
        
        if config_update.topics:
            config.TOPICS = config_update.topics
            updated_fields.append("topics")
        
        if config_update.max_articles_per_topic:
            config.MAX_ARTICLES_PER_TOPIC = config_update.max_articles_per_topic
            updated_fields.append("max_articles_per_topic")
        
        return {
            "message": "Configuration updated successfully",
            "updated_fields": updated_fields,
            "note": "Changes are runtime only. Update .env file for persistence."
        }
        
    except Exception as e:
        logger.error(f"Error updating configuration: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)