#!/bin/bash
# ============================================
# AgriAdvisory — One Command Setup
# Run this AFTER filling your .env file
# ============================================

set -e
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo ""
echo "=========================================="
echo "  AgriAdvisory — Automated Setup"
echo "=========================================="
echo ""

# Check .env exists
if [ ! -f ".env" ]; then
    echo -e "${RED}ERROR: .env file not found!${NC}"
    echo "Run: cp .env.example .env"
    echo "Then fill in your API keys"
    exit 1
fi

# Check if keys are still placeholder
if grep -q "your_gemini_key" .env 2>/dev/null; then
    echo -e "${RED}ERROR: .env still has placeholder values!${NC}"
    echo "Please fill in your real API keys in .env first"
    exit 1
fi

echo -e "${GREEN}[1/6]${NC} Installing backend dependencies..."
cd backend
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate 2>/dev/null || source venv/Scripts/activate 2>/dev/null
pip install -r requirements.txt --quiet
echo -e "${GREEN}      Done!${NC}"

echo ""
echo -e "${GREEN}[2/6]${NC} Training XGBoost crop prediction model..."
if [ ! -f "data/crop_data.csv" ]; then
    echo -e "${YELLOW}      Dataset included (pre-generated). For best results, replace with Kaggle dataset.${NC}"
fi
python ml/train_crop_model.py
echo -e "${GREEN}      Model trained!${NC}"

echo ""
echo -e "${GREEN}[3/6]${NC} Seeding Neo4j knowledge graph..."
python graph/seed_graph.py
echo -e "${GREEN}      Graph seeded!${NC}"

echo ""
echo -e "${GREEN}[4/6]${NC} Ingesting documents into Qdrant..."
python rag/ingest_docs.py
echo -e "${GREEN}      Knowledge base ready!${NC}"

echo ""
echo -e "${GREEN}[5/6]${NC} Installing frontend dependencies..."
cd ../frontend
npm install --silent 2>/dev/null || npm install
echo -e "${GREEN}      Frontend ready!${NC}"

echo ""
echo -e "${GREEN}[6/6]${NC} Verifying ML pipeline..."
cd ../backend
python3 -c "
from ml.predict_crop import predict_crop
from ml.shap_explainer import get_shap_explanation
r = predict_crop({'N':80,'P':48,'K':40,'temperature':24,'humidity':82,'ph':6.4,'rainfall':236})
s = get_shap_explanation({'N':80,'P':48,'K':40,'temperature':24,'humidity':82,'ph':6.4,'rainfall':236})
print(f'  Prediction: {r[\"predicted_crop\"]} ({r[\"confidence\"]}% confidence)')
print(f'  SHAP working: {len(s)} factors extracted')
print(f'  Top factor: {s[0][\"feature_label\"]}')
"
echo -e "${GREEN}      Pipeline verified!${NC}"

cd ..
echo ""
echo "=========================================="
echo -e "${GREEN}  SETUP COMPLETE!${NC}"
echo "=========================================="
echo ""
echo "  Start the app with TWO terminals:"
echo ""
echo "  Terminal 1 (Backend):"
echo "    cd backend && source venv/bin/activate"
echo "    uvicorn main:app --reload"
echo ""
echo "  Terminal 2 (Frontend):"
echo "    cd frontend"
echo "    npm run dev"
echo ""
echo "  Then open: http://localhost:5173"
echo ""
