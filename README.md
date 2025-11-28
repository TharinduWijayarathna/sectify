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

### With Docker (Recommended)

```bash
./docker-setup.sh
```

Then open http://localhost

### Manual Setup

**Backend:**
```bash
cd backend
./setup.sh
source venv/bin/activate
python main.py
```

**Frontend:**
```bash
cd frontend
./setup.sh
npm run dev
```

## Features

- ✅ Multiple file formats (PDF, DOCX, TXT)
- ✅ Smart section detection (headers, visual breaks, structure)
- ✅ ML-powered relevance scoring
- ✅ Named entity recognition (people, orgs, dates, money)
- ✅ Drag-and-drop interface
- ✅ Adjustable threshold filtering
- ✅ Batch processing
- ✅ Training mode (improve with feedback)
- ✅ Modern dark UI with animations

## How It Works

1. **Upload** → Document is parsed and text extracted
2. **Segment** → Split into logical sections using pattern detection
3. **Analyze** → Extract features (numbers, entities, structure)
4. **Score** → ML classifier rates relevance (0-100%)
5. **Filter** → Show sections above threshold
6. **Export** → Download as JSON or TXT

## Technology

- **Backend:** FastAPI, PyMuPDF, python-docx, spaCy, scikit-learn
- **Frontend:** React, Vite, Tailwind CSS
- **Deployment:** Docker, Docker Compose

## Documentation

- [DOCKER.md](DOCKER.md) - Complete Docker guide with deployment, troubleshooting
- [API Docs](http://localhost:8000/docs) - Interactive API documentation (when running)

## Project Structure

```
sectify/
├── backend/          # FastAPI + ML
├── frontend/         # React UI
├── docker-compose.yml
└── docker-setup.sh   # One-command setup
```

## Configuration

Edit `.env` or environment variables in `docker-compose.yml`:

```env
API_PORT=8000
DEFAULT_THRESHOLD=0.5
MIN_SECTION_LENGTH=20
```

## Contributing

Contributions welcome! The system uses:
- **Document Parser** - Handles PDF/DOCX/TXT
- **Section Segmenter** - Detects sections
- **Feature Extractor** - Analyzes text
- **ML Classifier** - Scores relevance (heuristics + Random Forest)

## License

MIT License

---

**Need help?** See [DOCKER.md](DOCKER.md) for detailed documentation.
