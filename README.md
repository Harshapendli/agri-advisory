# AgriAdvisory — Knowledge Graph-Based Agricultural Advisory System

AI-powered farming recommendations using XGBoost + Neo4j Knowledge Graph + GraphRAG + Gemini + Multilingual Voice.

## Quick Start

### Step 1 — Clone and setup
```bash
git clone <your-repo>
cd agri-advisory
cp .env.example .env
# Fill in your API keys in .env
```

### Step 2 — Fill API keys in .env
- **MONGO_URI** → mongodb.com/atlas (free M0 cluster)
- **NEO4J_URI / USER / PASSWORD** → neo4j.com/cloud/aura (free)
- **QDRANT_URL / API_KEY** → cloud.qdrant.io (free 1GB)
- **GEMINI_API_KEY** → aistudio.google.com
- **OPENWEATHER_API_KEY** → openweathermap.org/api

### Step 3 — Backend setup
```bash
cd backend
python -m venv venv && source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt
```

### Step 4 — Train the ML model
```bash
# Download dataset first:
# https://www.kaggle.com/datasets/atharvaingle/crop-recommendation-dataset
# Save as backend/data/crop_data.csv

python ml/train_crop_model.py
# Expected output: ~97% accuracy
```

### Step 5 — Seed the Knowledge Graph
```bash
python graph/seed_graph.py
# Creates 22 crops, 6 soils, 10 diseases, 8 fertilizers, 6 pesticides
# + all relationships in Neo4j AuraDB
```

### Step 6 — (Optional) Ingest docs into Qdrant
```bash
# Put any agricultural PDF/TXT files in backend/docs/
mkdir docs
# Add ICAR guidelines, crop bulletins etc.
python rag/ingest_docs.py
```

### Step 7 — Start backend
```bash
uvicorn main:app --reload
# API running at http://localhost:8000
# Docs at http://localhost:8000/docs
```

### Step 8 — Start frontend
```bash
cd ../frontend
cp ../.env.example .env.local
# Set VITE_API_URL=http://localhost:8000
npm install
npm run dev
# App running at http://localhost:5173
```

## Tech Stack

| Layer | Technology |
|-------|-----------|
| Backend | FastAPI + Python 3.11 |
| ML Prediction | XGBoost + SHAP |
| Knowledge Graph | Neo4j AuraDB |
| Vector Search | Qdrant Cloud |
| LLM | Gemini 1.5 Flash (LangChain) |
| Voice STT | OpenAI Whisper |
| Voice TTS | gTTS |
| Database | MongoDB Atlas (Beanie ODM) |
| Frontend | React 18 + TypeScript + Tailwind |
| Container | Docker + Docker Compose |

## Features
- Crop recommendation (XGBoost, 97% accuracy)
- SHAP explainability for every prediction
- Knowledge graph traversal (Neo4j AuraDB)
- GraphRAG pipeline (graph + vector + LLM)
- Multilingual voice chat (Telugu, Hindi, English, Marathi)
- Plant disease detection (CNN, mock mode until trained)
- Real-time weather integration
- Government scheme recommendations

## Project Structure
```
agri-advisory/
├── backend/          FastAPI backend
│   ├── ml/          XGBoost + SHAP models
│   ├── graph/       Neo4j client + seed data
│   ├── rag/         GraphRAG chain + Qdrant
│   ├── routers/     API endpoints
│   └── models/      MongoDB documents
└── frontend/        React + TypeScript UI
```
