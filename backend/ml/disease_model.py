import os
import json
from functools import lru_cache
from config import settings

DISEASE_CLASSES = [
    "Apple___Apple_scab", "Apple___Black_rot", "Apple___healthy",
    "Corn___Common_rust", "Corn___Northern_Leaf_Blight", "Corn___healthy",
    "Grape___Black_rot", "Grape___healthy",
    "Potato___Early_blight", "Potato___Late_blight", "Potato___healthy",
    "Rice___Leaf_Blight", "Rice___Brown_Spot", "Rice___healthy",
    "Tomato___Early_blight", "Tomato___Late_blight", "Tomato___Leaf_Mold",
    "Tomato___Bacterial_spot", "Tomato___healthy",
    "Wheat___Rust", "Wheat___healthy",
]

@lru_cache(maxsize=1)
def _load_model():
    model_path = settings.DISEASE_MODEL_PATH
    if not os.path.exists(model_path):
        return None
    import torch
    from torchvision import models
    model = models.efficientnet_b3(weights=None)
    num_classes = len(DISEASE_CLASSES)
    import torch.nn as nn
    model.classifier[1] = nn.Linear(model.classifier[1].in_features, num_classes)
    model.load_state_dict(torch.load(model_path, map_location="cpu"))
    model.eval()
    return model

class DiseaseModel:
    def __init__(self):
        self.model = _load_model()
        if self.model is None:
            raise FileNotFoundError("Disease model not trained. Using mock mode.")

    def predict(self, image_path: str) -> dict:
        import torch
        from torchvision import transforms
        from PIL import Image

        tfm = transforms.Compose([
            transforms.Resize(256),
            transforms.CenterCrop(224),
            transforms.ToTensor(),
            transforms.Normalize([0.485, 0.456, 0.406], [0.229, 0.224, 0.225]),
        ])
        img = Image.open(image_path).convert("RGB")
        x = tfm(img).unsqueeze(0)
        with torch.no_grad():
            logits = self.model(x)
            probs = torch.softmax(logits, dim=1)[0]
            idx = int(torch.argmax(probs))
        raw_name = DISEASE_CLASSES[idx]
        clean_name = raw_name.split("___")[1].replace("_", " ").title()
        return {
            "disease_name": clean_name,
            "confidence": round(float(probs[idx]) * 100, 2),
            "class_index": idx,
            "mock": False,
        }
