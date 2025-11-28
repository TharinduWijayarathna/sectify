# Sectify - NLP Document Section Extraction System

An AI-powered system for automatically extracting and identifying relevant sections from uploaded documents using Natural Language Processing and Machine Learning.

![Sectify](https://img.shields.io/badge/Python-3.9+-blue.svg)
![React](https://img.shields.io/badge/React-18+-61DAFB.svg)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-009688.svg)

## ✨ Features

- **Multi-Format Support**: Process PDF, DOCX, and TXT files
- **Smart Section Detection**: Automatically segments documents using pattern recognition
- **AI-Powered Relevance Scoring**: ML-based classification with heuristic fallback
- **Interactive UI**: Modern React interface with drag-and-drop upload
- **Real-time Filtering**: Adjustable relevance threshold slider
- **Training Mode**: Improve accuracy by providing feedback on sections
- **Batch Processing**: Upload and process multiple documents simultaneously
- **Export Results**: Download extracted sections as JSON or TXT
- **Feature Tagging**: Automatic detection of numbers, dates, entities, tables, and lists
- **Incremental Learning**: Model improves with user feedback

## 🏗️ Architecture

```
┌─────────────┐       ┌──────────────┐       ┌─────────────┐
│   Frontend  │──────▶│   FastAPI    │──────▶│   Modules   │
│   (React)   │◀──────│   Backend    │◀──────│   (Python)  │
└─────────────┘       └──────────────┘       └─────────────┘
                              │
                              ▼
                      ┌───────────────┐
                      │  ML Classifier │
                      │    (sklearn)   │
                      └───────────────┘
```

### Backend Components

- **Document Parser**: Extracts text from PDF (PyMuPDF), DOCX (python-docx), and TXT files
- **Section Segmenter**: Splits documents using regex patterns and structural analysis
- **Feature Extractor**: Analyzes sections for numerical data, entities, and structure
- **Relevance Classifier**: Scores sections using ML (when trained) or heuristics
- **FastAPI Server**: RESTful API with endpoints for upload, results, feedback, and export

### Frontend Components

- **DocumentUpload**: Drag-and-drop interface with batch processing
- **SectionDisplay**: Interactive results viewer with filtering and expansion
- **Training Mode**: Feedback collection interface for model improvement

## 🚀 Quick Start

### Prerequisites

- Python 3.9 or higher
- Node.js 18 or higher
- npm or yarn

### Backend Setup

```bash
# Navigate to backend directory
cd backend

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Download spaCy model
python -m spacy download en_core_web_sm

# Copy environment file
cp ../.env.example .env

# Run the server
python main.py
```

The backend will start at `http://localhost:8000`

### Frontend Setup

```bash
# Navigate to frontend directory
cd frontend

# Install dependencies
npm install

# Start development server
npm run dev
```

The frontend will start at `http://localhost:5173`

## 📖 Usage

### 1. Upload a Document

- Drag and drop a PDF, DOCX, or TXT file onto the upload area
- Or click to browse and select a file
- Optionally enable **Batch Mode** to upload multiple files
- Adjust the **Relevance Threshold** (default: 0.5)

### 2. View Results

- See all extracted sections with relevance scores
- Sections are color-coded:
  - 🟢 Green (≥70%): Highly relevant
  - 🟡 Yellow (40-69%): Moderately relevant
  - 🔴 Red (<40%): Less relevant
- Click on sections to expand and read full content
- View feature tags (numbers, dates, entities, etc.)

### 3. Filter Sections

- Use the threshold slider to show/hide sections
- Higher threshold = only show more relevant sections
- Lower threshold = include borderline sections

### 4. Train the Model

- Enable **Training Mode**
- Review each section and mark as relevant or not
- The model will improve with your feedback
- After 10+ examples, the system automatically retrains

### 5. Export Results

- Click **JSON** to export as structured data
- Click **TXT** to export as plain text
- Exports respect the current threshold filter

## 🎯 API Documentation

### Endpoints

#### `POST /api/upload`

Upload and process a document.

**Parameters:**
- `file`: Document file (multipart/form-data)
- `threshold`: Relevance threshold (0.0-1.0, default: 0.5)

**Response:**
```json
{
  "document_id": "abc123...",
  "filename": "report.pdf",
  "status": "success",
  "message": "Processed 15 sections, 8 relevant"
}
```

#### `GET /api/documents/{document_id}`

Get processing results for a document.

**Query Parameters:**
- `threshold`: Optional threshold to refilter results

**Response:**
```json
{
  "document_id": "abc123...",
  "document_name": "report.pdf",
  "total_sections": 15,
  "relevant_sections": 8,
  "sections": [...],
  "processing_time": 2.34,
  "threshold": 0.5
}
```

#### `POST /api/feedback`

Submit section feedback for training.

**Body:**
```json
{
  "document_id": "abc123...",
  "section_id": 1,
  "is_relevant": true
}
```

#### `POST /api/batch`

Upload multiple documents.

**Parameters:**
- `files`: Array of document files
- `threshold`: Relevance threshold

#### `POST /api/export`

Export document results.

**Body:**
```json
{
  "document_id": "abc123...",
  "format": "json",
  "threshold": 0.5
}
```

#### `GET /api/health`

Health check endpoint.

## 🧪 Testing

### Backend Tests

```bash
cd backend
pytest tests/ -v --cov=. --cov-report=html
```

### Test with Sample Documents

```bash
# Create a test directory
mkdir test_docs

# Add some sample PDFs/DOCX/TXT files
# Then upload via the UI or use curl:

curl -X POST "http://localhost:8000/api/upload" \
  -F "file=@test_docs/sample.pdf" \
  -F "threshold=0.5"
```

## 🔧 Configuration

Create a `.env` file in the root directory:

```env
# API Configuration
API_HOST=0.0.0.0
API_PORT=8000

# CORS Settings
CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Storage Paths
UPLOAD_DIR=./uploads
MODEL_DIR=./models

# spaCy Configuration
SPACY_MODEL=en_core_web_sm

# ML Configuration
DEFAULT_THRESHOLD=0.5
MIN_SECTION_LENGTH=20
```

## 📊 How It Works

### Section Scoring Algorithm

1. **Feature Extraction**
   - Word count, sentence count
   - Numerical indicators (digits, currencies, percentages)
   - Named entities (people, organizations, dates, locations)
   - Structural elements (tables, lists, bullet points)
   - Text density and position

2. **Heuristic Scoring** (Zero-shot mode)
   - Weighted combination of features
   - High scores for data-rich sections
   - Penalties for very short or boilerplate text

3. **ML Scoring** (Trained mode)
   - Random Forest Classifier
   - Trained on user feedback
   - Feature normalization and scaling
   - Confidence-based predictions

### Section Detection Patterns

- Numbered sections: `1.`, `1.1.`, `1.1.1.`
- Roman numerals: `I.`, `II.`, `III.`
- Lettered sections: `A.`, `B.`, `C.`
- ALL CAPS headers
- Title Case headers
- Visual breaks (lines, page breaks)

## 🎨 Design Features

- **Dark Mode**: Sleek dark theme with purple gradients
- **Glassmorphism**: Modern frosted glass effects
- **Smooth Animations**: Micro-interactions and transitions
- **Responsive**: Works on desktop, tablet, and mobile
- **Accessibility**: Keyboard navigation and screen reader support

## 🛠️ Technology Stack

**Backend:**
- FastAPI - Modern web framework
- PyMuPDF - PDF parsing
- python-docx - Word document parsing
- spaCy - NLP and entity recognition
- scikit-learn - Machine learning
- Pydantic - Data validation

**Frontend:**
- React 18 - UI framework
- Vite - Build tool
- Tailwind CSS - Styling
- Lucide React - Icons
- React Dropzone - File upload
- Axios - HTTP client

## 🚧 Future Enhancements

- [ ] OCR support for scanned PDFs
- [ ] Semantic search across sections
- [ ] Document comparison mode
- [ ] PDF highlighting export
- [ ] Advanced ML models (transformers)
- [ ] Multi-language support
- [ ] Cloud deployment
- [ ] Docker containerization
- [ ] Database integration
- [ ] User authentication

## 📝 License

MIT License - feel free to use this project for any purpose.

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 📧 Support

For issues and questions, please open an issue on the repository.

---

**Built with ❤️ using FastAPI, React, spaCy, and scikit-learn**
