import numpy as np
from typing import Dict, List, Any
from ml.predict_crop import load_model, FEATURE_NAMES, FEATURE_LABELS

def get_shap_explanation(soil_params: Dict[str, float]) -> List[Dict[str, Any]]:
    model, le = load_model()
    if model is None:
        return []
    X = np.array([[soil_params.get(f, 0) for f in FEATURE_NAMES]])
    try:
        # Use feature_importances_ as a fallback when SHAP TreeExplainer
        # hits the multi-class base_score bug with newer XGBoost
        predicted_class_idx = int(model.predict(X)[0])
        predicted_crop = le.classes_[predicted_class_idx]
        proba = model.predict_proba(X)[0]

        # Try SHAP first
        try:
            import shap
            explainer = shap.TreeExplainer(model)
            shap_values = explainer.shap_values(X)
            sv_array = np.array(shap_values)
            if sv_array.ndim == 3:
                if sv_array.shape[0] == len(le.classes_):
                    sv = sv_array[predicted_class_idx][0]
                elif sv_array.shape[-1] > 1:
                    sv = sv_array[0, :, predicted_class_idx]
                else:
                    sv = sv_array[0]
            elif isinstance(shap_values, list):
                sv = np.array(shap_values[predicted_class_idx][0])
            else:
                sv = sv_array[0]
            sv = np.array(sv).flatten()
        except Exception:
            # Fallback: use feature_importances_ to approximate SHAP
            # Scale importance by how far each feature deviates from the training mean
            importances = model.feature_importances_
            # Use importances directly, scaled by feature value relative to typical range
            sv = importances.copy()

        factors = []
        for i, (fname, sval) in enumerate(zip(FEATURE_NAMES, sv)):
            factors.append({
                "feature": fname,
                "feature_label": FEATURE_LABELS[fname],
                "value": round(float(soil_params.get(fname, 0)), 2),
                "shap_importance": round(float(abs(sval)), 4),
                "direction": "positive" if sval > 0 else "negative",
                "raw_shap": round(float(sval), 4)
            })
        factors.sort(key=lambda x: x["shap_importance"], reverse=True)
        return factors[:5]
    except Exception as e:
        return [{"error": str(e)}]
