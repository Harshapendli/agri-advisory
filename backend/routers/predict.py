from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any
from ml.predict_crop import predict_crop
from ml.shap_explainer import get_shap_explanation

router = APIRouter(prefix="/predict", tags=["prediction"])

class SoilInput(BaseModel):
    N: float = Field(..., ge=0, le=140)
    P: float = Field(..., ge=0, le=145)
    K: float = Field(..., ge=0, le=205)
    temperature: float = Field(..., ge=0, le=50)
    humidity: float = Field(..., ge=0, le=100)
    ph: float = Field(..., ge=0, le=14)
    rainfall: float = Field(..., ge=0, le=300)

@router.post("/crop")
async def predict_crop_endpoint(soil: SoilInput):
    soil_dict = soil.model_dump()
    result = predict_crop(soil_dict)
    if result.get("error"):
        raise HTTPException(status_code=503, detail=result["error"])
    shap_factors = get_shap_explanation(soil_dict)
    return {**result, "shap_factors": shap_factors, "soil_params": soil_dict}
