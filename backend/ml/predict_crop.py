import joblib
import numpy as np
import os
from functools import lru_cache
from typing import Dict, List, Any
from config import settings

FEATURE_NAMES = ["N", "P", "K", "temperature", "humidity", "ph", "rainfall"]
FEATURE_LABELS = {
    "N": "Nitrogen", "P": "Phosphorus", "K": "Potassium",
    "temperature": "Temperature", "humidity": "Humidity",
    "ph": "Soil pH", "rainfall": "Rainfall"
}

@lru_cache(maxsize=1)
def load_model():
    model_path = settings.MODEL_PATH
    encoder_path = settings.LABEL_ENCODER_PATH
    if not os.path.exists(model_path):
        return None, None
    model = joblib.load(model_path)
    le = joblib.load(encoder_path)
    return model, le

def predict_crop(soil_params: Dict[str, float]) -> Dict[str, Any]:
    model, le = load_model()
    if model is None:
        return {
            "error": "Model not trained yet. Run: python ml/train_crop_model.py",
            "predicted_crop": None, "confidence": 0, "alternatives": []
        }
    X = np.array([[soil_params.get(f, 0) for f in FEATURE_NAMES]])
    proba = model.predict_proba(X)[0]
    top3_idx = np.argsort(proba)[::-1][:3]
    predicted_crop = le.classes_[top3_idx[0]]
    confidence = float(proba[top3_idx[0]])
    alternatives = [
        {"crop": le.classes_[i], "confidence": float(proba[i])}
        for i in top3_idx[1:]
    ]
    return {
        "predicted_crop": predicted_crop,
        "confidence": round(confidence * 100, 2),
        "alternatives": [{"crop": a["crop"], "confidence": round(a["confidence"] * 100, 2)} for a in alternatives],
        "error": None
    }
