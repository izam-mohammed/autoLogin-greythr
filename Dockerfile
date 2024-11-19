FROM python:3.10-slim
WORKDIR /app

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libasound2 \
    libpango-1.0-0 \
    libcairo2 \
    build-essential \
    gcc \
    libpq-dev && \
    rm -rf /var/lib/apt/lists/*

RUN curl -sSL https://install.python-poetry.org | python3 - && \
    cd /usr/local/bin && \
    ln -s /root/.local/bin/poetry && \
    poetry config virtualenvs.create false

ENV PATH="/root/.local/bin:$PATH"

COPY pyproject.toml poetry.lock* ./

RUN poetry install --no-dev --no-interaction --no-ansi

RUN poetry run playwright install chromium && \
    poetry run playwright install-deps

COPY main.py ./

CMD ["poetry", "run", "python", "main.py"]
