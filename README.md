# Login Automation

Automated login and attendance marking system using Playwright and Docker.

## Setup

1. Create `.env` file:
```env
username=your_username
password=your_password
base_url=https://{company_id}.greythr.com/
```

2. Run with Docker:
```bash
docker-compose up --build
```

## Features

- Automated login with cookie persistence
- Runs on weekdays between 8 AM - 1 PM (IST)
- Takes screenshot after each attempt
- Headless browser automation

## File Structure
```
├── Dockerfile
├── docker-compose.yml
├── pyproject.toml
├── poetry.lock
├── main.py
├── .env
├── cookies.json (generated)
└── login_proof.png (generated)
```

## Local Development

```bash
poetry install
poetry run playwright install chromium
poetry run playwright install-deps
poetry run python main.py
```

## Logs
- Located in Docker logs
- Max size: 10MB, 3 files rotation