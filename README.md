# Sectify

AI-powered document section extraction using NLP and Machine Learning.

![Python](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)
![Docker](https://img.shields.io/badge/Docker-Ready-2496ED.svg)

## What It Does

Upload PDF, DOCX, or TXT documents and automatically:
- 📄 Extract and segment sections
- 🤖 Score relevance using ML and NLP
- 🎯 Filter important content from boilerplate
- 📊 Export results as JSON or text
- 🧠 Learn from your feedback to improve accuracy

## Quick Start

```bash
make up
```

Then open http://localhost

## Requirements

- Docker & Docker Compose
- That's it! No local Python or Node.js needed.

## Development

Run in development mode with hot reload:

```bash
docker-compose -f docker-compose.dev.yml up
```

## Other Commands

**Stop the app:**
```bash
make down
```

**Clean uploads and models:**
```bash
make clean
```

## Configuration

Copy `.env.example` to `.env` and customize settings:

```bash
cp .env.example .env
```

## Contributing

You can contribute to this project by submitting issues or pull requests.