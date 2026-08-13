@echo off
REM ============================================
REM AgriAdvisory — Windows Setup
REM Run this AFTER filling your .env file
REM ============================================

echo.
echo ==========================================
echo   AgriAdvisory — Automated Setup
echo ==========================================
echo.

if not exist ".env" (
    echo ERROR: .env file not found!
    echo Run: copy .env.example .env
    echo Then fill in your API keys
    pause
    exit /b 1
)

echo [1/6] Installing backend dependencies...
cd backend
if not exist "venv" python -m venv venv
call venv\Scripts\activate.bat
pip install -r requirements.txt --quiet
echo       Done!

echo.
echo [2/6] Training XGBoost model...
python ml\train_crop_model.py
echo       Done!

echo.
echo [3/6] Seeding Neo4j knowledge graph...
python graph\seed_graph.py
echo       Done!

echo.
echo [4/6] Ingesting docs into Qdrant...
python rag\ingest_docs.py
echo       Done!

echo.
echo [5/6] Installing frontend...
cd ..\frontend
call npm install
echo       Done!

echo.
echo [6/6] Verifying ML pipeline...
cd ..\backend
python -c "from ml.predict_crop import predict_crop; r=predict_crop({'N':80,'P':48,'K':40,'temperature':24,'humidity':82,'ph':6.4,'rainfall':236}); print(f'Prediction: {r[\"predicted_crop\"]} ({r[\"confidence\"]}%%)')"
echo       Done!

cd ..
echo.
echo ==========================================
echo   SETUP COMPLETE!
echo ==========================================
echo.
echo   Terminal 1: cd backend ^& venv\Scripts\activate ^& uvicorn main:app --reload
echo   Terminal 2: cd frontend ^& npm run dev
echo   Open: http://localhost:5173
echo.
pause
