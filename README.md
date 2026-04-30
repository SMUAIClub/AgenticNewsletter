# 24/7 AI Newsletter Agent 🤖📧



https://github.com/user-attachments/assets/c1cfb8bb-b195-4446-8fef-9bb7278ea797





An intelligent, automated newsletter generation system that crawls the web for AI and tech news, processes it through multiple AI agents, and delivers personalized newsletters via email.

## 🚀 Features

- **Automated Web Crawling**: Uses Crawl4AI to gather real-time news from multiple sources
- **Multi-Agent Processing**: LangGraph orchestrates different AI agents (Research, Analysis, Opinion, Editor)
- **Smart Scheduling**: Configurable schedule for automatic newsletter generation
- **Email Delivery**: Gmail API integration for professional email delivery
- **Web Dashboard**: FastAPI-based monitoring and management interface
- **Docker Support**: Easy deployment with Docker containers
- **Extensible Architecture**: Modular design for easy customization

## 🏗️ Architecture

```
┌─────────────────┐    ┌──────────────────┐    ┌─────────────────┐
│   Scheduler     │───▶│   Web Crawler    │───▶│  Multi-Agent    │
│   (schedule)    │    │   (Crawl4AI)     │    │  (LangGraph)    │
└─────────────────┘    └──────────────────┘    └─────────────────┘
                                                         │
┌─────────────────┐    ┌──────────────────┐             │
│  Email Service  │◀───│   Newsletter     │◀────────────┘
│  (Gmail API)    │    │   Formatter      │
└─────────────────┘    └──────────────────┘
```

## 📦 Installation

### Prerequisites

- Python 3.11+
- OpenRouter API key
- Gmail API credentials
- Docker (optional)

### Quick Start

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd Newsletter_aaa
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env with your API keys and configuration
   ```

4. **Set up Gmail API**
   - Go to [Google Cloud Console](https://console.cloud.google.com/)
   - Create a new project or select existing one
   - Enable Gmail API
   - Create credentials (OAuth 2.0 Client ID)
   - Download `credentials.json` to project root

5. **Run the application**
   ```bash
   # Run once
   python main.py --mode once
   
   # Start scheduler
   python main.py --mode schedule
   
   # Check configuration
   python main.py --config-check
   ```

## ⚙️ Configuration

### Environment Variables (.env)

```env
# OpenRouter API Configuration
OPENROUTER_API_KEY=your_openrouter_api_key_here
OPENROUTER_BASE_URL=https://openrouter.ai/api/v1

# Gmail API Configuration
GMAIL_CREDENTIALS_PATH=credentials.json
GMAIL_TOKEN_PATH=token.json

# Newsletter Configuration
SENDER_EMAIL=your_email@gmail.com
RECIPIENT_EMAILS=recipient1@example.com,recipient2@example.com
NEWSLETTER_TITLE=Daily AI Newsletter

# Scheduling Configuration
SCHEDULE_TIMES=08:00,18:00
TIMEZONE=Asia/Kolkata

# Crawling Configuration
MAX_ARTICLES_PER_TOPIC=5
CRAWL_TIMEOUT=30

# LLM Configuration
DEFAULT_MODEL=gpt-4-turbo-preview
TEMPERATURE=0.7
MAX_TOKENS=2000
```

### Topics Configuration

Edit `config.py` to customize topics:

```python
TOPICS = [
    "AI news",
    "Machine Learning breakthroughs",
    "Tech startups",
    "OpenAI updates",
    "Google AI developments",
    "Tech industry trends"
]
```

## 🐳 Docker Deployment

### Using Docker Compose (Recommended)

```bash
# Build and start services
docker-compose -f docker/docker-compose.yml up -d

# View logs
docker-compose -f docker/docker-compose.yml logs -f

# Stop services
docker-compose -f docker/docker-compose.yml down
```

### Manual Docker Build

```bash
# Build image
docker build -f docker/Dockerfile -t ai-newsletter-agent .

# Run container
docker run -d \
  --name newsletter-agent \
  --env-file .env \
  -v $(pwd)/logs:/app/logs \
  -v $(pwd)/credentials.json:/app/credentials.json:ro \
  -p 8000:8000 \
  ai-newsletter-agent
```

## 🌐 Web Dashboard

Access the web dashboard at `http://localhost:8000` when running the FastAPI server:

```bash
# Start API server
python -m uvicorn api.fastapi_server:app --host 0.0.0.0 --port 8000
```

### API Endpoints

- `GET /` - Dashboard homepage
- `GET /status` - System status
- `POST /generate` - Generate newsletter immediately
- `GET /history` - Newsletter generation history
- `POST /schedule/start` - Start scheduler
- `POST /schedule/stop` - Stop scheduler
- `GET /config` - Get configuration
- `POST /config` - Update configuration
- `GET /health` - Health check

## 🔧 Usage Examples

### Command Line

```bash
# Generate newsletter once
python main.py --mode once

# Start scheduled service
python main.py --mode schedule

# Check configuration
python main.py --config-check
```

### API Usage

```bash
# Generate newsletter via API
curl -X POST http://localhost:8000/generate

# Check status
curl http://localhost:8000/status

# Start scheduler
curl -X POST http://localhost:8000/schedule/start
```

### Python Integration

```python
from scheduler.newsletter_scheduler import NewsletterScheduler

# Create scheduler instance
scheduler = NewsletterScheduler()

# Run once
scheduler.run_once()

# Start scheduled service
scheduler.start_scheduler()
```

## 🧩 Architecture Components

### 1. Web Crawler (`crawlers/web_crawler.py`)
- Uses Crawl4AI for intelligent web scraping
- Supports RSS feeds and direct URL crawling
- Filters content by relevance and recency

### 2. Multi-Agent System (`agents/newsletter_agents.py`)
- **Research Agent**: Categorizes and summarizes articles
- **Analysis Agent**: Provides deep insights and implications
- **Opinion Agent**: Adds editorial commentary
- **Editor Agent**: Compiles final newsletter with formatting

### 3. LLM Client (`agents/llm_client.py`)
- OpenRouter API integration
- Retry logic and error handling
- Configurable models and parameters

### 4. Email Service (`email_service/gmail_client.py`)
- Gmail API integration
- HTML email formatting
- Batch sending support

### 5. Scheduler (`scheduler/newsletter_scheduler.py`)
- Configurable scheduling
- Async workflow orchestration
- Error handling and logging

## 📊 Monitoring and Logging

- Logs are stored in `logs/` directory
- Daily log rotation
- Structured logging with timestamps
- Health check endpoints for monitoring

## 🔒 Security Considerations

- API keys stored in environment variables
- OAuth 2.0 for Gmail API authentication
- No sensitive data in logs
- Docker secrets support

## 🚀 Scaling and Production

### Performance Optimization
- Async/await for concurrent operations
- Connection pooling for HTTP requests
- Caching for frequently accessed data

### Production Deployment
- Use environment-specific configurations
- Set up monitoring and alerting
- Configure log aggregation
- Use a process manager (PM2, systemd)
- Set up reverse proxy (nginx)

### Monitoring
- Health check endpoints
- Metrics collection
- Error tracking
- Performance monitoring

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## 📝 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Troubleshooting

### Common Issues

1. **Gmail API Authentication**
   - Ensure `credentials.json` is in the project root
   - Check OAuth consent screen configuration
   - Verify Gmail API is enabled

2. **OpenRouter API Issues**
   - Verify API key is correct
   - Check rate limits
   - Ensure sufficient credits

3. **Crawling Issues**
   - Some sites may block automated requests
   - Adjust timeout settings
   - Check network connectivity

4. **Scheduling Issues**
   - Verify timezone configuration
   - Check system time
   - Review log files for errors

### Debug Mode

```bash
# Enable debug logging
export LOG_LEVEL=DEBUG
python main.py --mode once
```

## 📞 Support

For issues and questions:
- Check the logs in `logs/` directory
- Review configuration settings
- Check API credentials and permissions
- Consult the troubleshooting section

---

Built with ❤️ using Python, Crawl4AI, LangGraph, OpenRouter, and Gmail API.
