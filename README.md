# 24/7 AI Newsletter Agent

https://github.com/user-attachments/assets/c1cfb8bb-b195-4446-8fef-9bb7278ea797

An automated newsletter generation system that crawls the web for AI and tech news, processes it through a multi-agent LangGraph pipeline, and produces a polished newsletter.

## Features

- **Web Crawling** — Crawl4AI + DuckDuckGo search to find fresh articles for each topic
- **Multi-Agent Pipeline** — LangGraph orchestrates Research → Analysis → Opinion → Editor agents
- **OpenAI Powered** — Uses `gpt-4o` by default, fully configurable
- **Web Dashboard** — FastAPI server for triggering runs and viewing history
- **Scheduler** — Runs on a configurable daily schedule
- **Docker Support** — Single command to run everything in a container

## Architecture

```
Scheduler
   │
   ▼
Web Crawler (Crawl4AI)
   │  fetches articles per topic
   ▼
LangGraph Agent Pipeline
   ├── Researcher  →  categorizes & summarizes
   ├── Analyst     →  insights & implications
   ├── Opinion     →  editorial commentary
   └── Editor      →  final formatted newsletter
```

---

## Quickstart (Docker)

**Prerequisites:** Docker + Docker Compose

```bash
# 1. Make sure .env exists with your OpenAI key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 2. Build and start (scheduler + API server)
docker compose -f docker/docker-compose.yml up -d --build

# 3. View live logs
docker compose -f docker/docker-compose.yml logs -f

# 4. Stop
docker compose -f docker/docker-compose.yml down
```

| Service | URL |
|---|---|
| API / Dashboard | http://localhost:8001 |

> Note: The first build takes a few minutes — it installs Chromium inside the image.

### Trigger a newsletter generation

```bash
curl -X POST http://localhost:8001/generate
```

The output is saved to `newsletters/newsletter_<timestamp>.md` in the project folder.

### Single container (run once)

```bash
docker build -f docker/Dockerfile -t ai-newsletter .
docker run --env-file .env -v $(pwd)/logs:/app/logs ai-newsletter \
  python main.py --mode once
```

---

## Quickstart (Local)

**Prerequisites:** Python 3.11+

```bash
# 1. Clone and enter the repo
git clone <repository-url>
cd AgenticNewsletter

# 2. Create a virtual environment
python3 -m venv venv
source venv/bin/activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Install Chromium for the web crawler (one-time)
crawl4ai-setup

# 5. Add your OpenAI API key
cp .env.example .env
# Edit .env and set OPENAI_API_KEY=sk-...

# 6. Verify config
python main.py --config-check

# 7. Run a single newsletter generation
python main.py --mode once
```

Logs are written to `logs/`. The generated newsletter content appears there.

### Run the web dashboard

```bash
uvicorn api.fastapi_server:app --reload --port 8000
```

Open `http://localhost:8000` to trigger runs, view history, and manage config.

---

## Configuration

### Environment variables (`.env`)

```env
# Required
OPENAI_API_KEY=sk-...

# Optional — shown with defaults
NEWSLETTER_TITLE=Daily AI Newsletter
SCHEDULE_TIMES=08:00,18:00
TIMEZONE=Asia/Kolkata
MAX_ARTICLES_PER_TOPIC=5
CRAWL_TIMEOUT=30
DEFAULT_MODEL=gpt-4o
TEMPERATURE=0.7
MAX_TOKENS=2000
```

### Topics

Edit `config.py` to change what gets crawled:

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

---

## Run Modes

```bash
python main.py --mode once      # generate once and exit
python main.py --mode schedule  # run on SCHEDULE_TIMES continuously
python main.py --config-check   # validate config and exit
```

## API Endpoints

| Method | Path | Description |
|---|---|---|
| `GET` | `/` | Dashboard |
| `GET` | `/status` | System status |
| `POST` | `/generate` | Trigger generation |
| `GET` | `/history` | Last 10 runs |
| `POST` | `/schedule/start` | Start scheduler |
| `POST` | `/schedule/stop` | Stop scheduler |
| `GET` | `/config` | Current config |
| `POST` | `/config` | Update config (runtime) |
| `GET` | `/health` | Health check |

```bash
# Examples
curl -X POST http://localhost:8000/generate
curl http://localhost:8000/status
```

---

## Troubleshooting

**Crawling fails / empty articles**
- Some sites block automated requests — the crawler falls back to `httpx` automatically
- Increase `CRAWL_TIMEOUT` in `.env`

**OpenAI errors**
- Double-check `OPENAI_API_KEY` in `.env`
- Verify you have quota/credits on the key

**Playwright not found (local)**
- Run `crawl4ai-setup` inside your activated virtual environment

**Docker build slow**
- Normal on first build; Chromium download is ~200MB. Subsequent builds use the cache layer.
