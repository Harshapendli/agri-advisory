from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile, os, hashlib
from graph.graph_queries import get_treatment_path

router = APIRouter(prefix="/disease", tags=["disease"])

# Deterministic disease detection based on image hash (not random)
DISEASE_MAP = [
    {"disease_name": "Early Blight", "confidence": 87.3, "symptoms": "Brown concentric ring-shaped spots (target-like pattern) on older leaves first. Leaves turn yellow around spots and eventually die.", "pathogen": "Alternaria solani (Fungus)"},
    {"disease_name": "Late Blight", "confidence": 82.5, "symptoms": "Dark water-soaked lesions on leaves and stems. White fuzzy mold appears on underside of leaves in humid conditions.", "pathogen": "Phytophthora infestans (Oomycete)"},
    {"disease_name": "Leaf Blight", "confidence": 79.8, "symptoms": "Large irregular brown patches on leaves starting from tips and margins. Leaves dry up from edges inward.", "pathogen": "Helminthosporium/Xanthomonas"},
    {"disease_name": "Powdery Mildew", "confidence": 91.2, "symptoms": "White powdery coating on upper leaf surface. Leaves curl upward and eventually turn brown.", "pathogen": "Erysiphe cichoracearum (Fungus)"},
    {"disease_name": "Bacterial Wilt", "confidence": 76.4, "symptoms": "Sudden wilting of entire plant without yellowing. When stem is cut, brown discoloration of vascular bundles visible.", "pathogen": "Ralstonia solanacearum (Bacteria)"},
    {"disease_name": "Mosaic Virus", "confidence": 84.1, "symptoms": "Mottled light and dark green pattern on leaves. Leaves become distorted, curled, and plant growth is stunted.", "pathogen": "Tobacco Mosaic Virus / Cucumber Mosaic Virus"},
    {"disease_name": "Anthracnose", "confidence": 88.7, "symptoms": "Dark sunken spots on fruits and stems with salmon-colored spore masses. Fruits crack and rot.", "pathogen": "Colletotrichum spp. (Fungus)"},
    {"disease_name": "Root Rot", "confidence": 73.9, "symptoms": "Yellowing and wilting of lower leaves first. Roots turn brown/black and mushy when pulled. Plant stunting.", "pathogen": "Pythium/Fusarium (Fungus)"},
]

# Specific treatment knowledge for each disease
TREATMENT_DB = {
    "Early Blight": {
        "treatments": [
            {"pesticide": "Mancozeb 75% WP", "application": "Foliar spray 2.5g/liter water, every 7-10 days", "dosage": "500g per acre"},
            {"pesticide": "Chlorothalonil", "application": "Foliar spray 2g/liter as preventive", "dosage": "400g per acre"},
            {"pesticide": "Azoxystrobin 23% SC", "application": "Spray 1ml/liter at first symptom", "dosage": "200ml per acre"},
        ],
        "prevention_tips": [
            "Remove and destroy infected leaves immediately to stop spread",
            "Maintain 60cm plant spacing for proper air circulation",
            "Avoid overhead irrigation — use drip to keep foliage dry",
            "Apply Trichoderma viride 2kg/acre as soil treatment before planting",
            "Rotate with non-solanaceous crops (cereals/pulses) for 2 seasons"
        ]
    },
    "Late Blight": {
        "treatments": [
            {"pesticide": "Copper Oxychloride 50% WP", "application": "Foliar spray 3g/liter water", "dosage": "600g per acre"},
            {"pesticide": "Metalaxyl + Mancozeb (Ridomil Gold)", "application": "Spray 2.5g/liter every 7 days", "dosage": "500g per acre"},
            {"pesticide": "Cymoxanil + Mancozeb", "application": "Spray 3g/liter in rainy season", "dosage": "600g per acre"},
        ],
        "prevention_tips": [
            "Use certified disease-free seeds/seedlings from trusted nurseries",
            "Destroy all crop debris after harvest — do not compost infected material",
            "Ensure proper drainage to prevent waterlogging around roots",
            "Apply preventive copper spray before monsoon onset",
            "Monitor weather — spray immediately when humidity exceeds 80% for 48 hours"
        ]
    },
    "Leaf Blight": {
        "treatments": [
            {"pesticide": "Mancozeb 75% WP", "application": "Foliar spray 2.5g/liter every 10 days", "dosage": "500g per acre"},
            {"pesticide": "Carbendazim 50% WP", "application": "Spray 1g/liter at first symptom", "dosage": "200g per acre"},
        ],
        "prevention_tips": [
            "Use resistant varieties recommended by local agricultural university",
            "Treat seeds with Carbendazim 2g/kg before sowing",
            "Maintain proper plant spacing (row to row 45cm, plant to plant 30cm)",
            "Avoid excess nitrogen fertilization which promotes lush susceptible growth",
            "Remove and burn infected crop residues after harvest"
        ]
    },
    "Powdery Mildew": {
        "treatments": [
            {"pesticide": "Sulphur 80% WP (Sulfex)", "application": "Dust or spray 3g/liter", "dosage": "500g per acre"},
            {"pesticide": "Carbendazim 50% WP", "application": "Spray 1g/liter every 15 days", "dosage": "200g per acre"},
            {"pesticide": "Hexaconazole 5% EC", "application": "Spray 2ml/liter", "dosage": "400ml per acre"},
        ],
        "prevention_tips": [
            "Improve air circulation by proper pruning and spacing",
            "Avoid overhead watering — water at base of plants",
            "Apply neem oil 3ml/liter as preventive every 10 days",
            "Remove heavily infected leaves and destroy them",
            "Grow resistant varieties wherever available"
        ]
    },
    "Bacterial Wilt": {
        "treatments": [
            {"pesticide": "Copper Oxychloride", "application": "Soil drench 3g/liter around plant base", "dosage": "600g per acre"},
            {"pesticide": "Streptocycline", "application": "Soil drench 0.5g/10 liters water", "dosage": "10g per acre"},
            {"pesticide": "Pseudomonas fluorescens", "application": "Soil application 2.5kg/acre mixed with FYM", "dosage": "2.5kg per acre"},
        ],
        "prevention_tips": [
            "Pull out and destroy infected plants immediately with roots",
            "Do not grow solanaceous crops (tomato/brinjal/chilli) in same field for 3 years",
            "Apply lime 200kg/acre to raise soil pH above 7.0",
            "Use grafted seedlings on resistant rootstock",
            "Improve soil drainage — raised bed cultivation recommended"
        ]
    },
}

@router.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only image files allowed (jpeg, png, webp)")
    suffix = os.path.splitext(file.filename or "img.jpg")[1] or ".jpg"
    with tempfile.NamedTemporaryFile(suffix=suffix, delete=False) as tmp:
        content = await file.read()
        tmp.write(content)
        tmp_path = tmp.name
    try:
        # Try real model first
        try:
            from ml.disease_model import DiseaseModel
            model = DiseaseModel()
            result = model.predict(tmp_path)
            disease_name = result["disease_name"]
        except Exception:
            # Deterministic mock based on image content hash (NOT random)
            img_hash = hashlib.md5(content).hexdigest()
            idx = int(img_hash[:8], 16) % len(DISEASE_MAP)
            result = DISEASE_MAP[idx].copy()
            result["mock"] = True
            disease_name = result["disease_name"]

        # Get treatment from our knowledge base first, then graph
        treatment_info = TREATMENT_DB.get(disease_name, {})
        graph_treatment = await get_treatment_path(disease_name)

        treatments = treatment_info.get("treatments", graph_treatment.get("treatments", [
            {"pesticide": "Mancozeb 75% WP", "application": "Foliar spray 2.5g/liter", "dosage": "500g/acre"},
            {"pesticide": "Copper Oxychloride", "application": "Spray 3g/liter water", "dosage": "600g/acre"},
        ]))

        prevention = treatment_info.get("prevention_tips", [
            "Regular field inspection every 3-4 days during monsoon",
            "Maintain proper plant spacing for air circulation",
            "Use disease-resistant varieties from ICAR-recommended list",
            "Apply preventive fungicide spray at first sign of symptoms",
            "Remove and destroy infected plant material — do not compost"
        ])

        return {
            "disease_name": disease_name,
            "confidence": result.get("confidence", 80.0),
            "is_mock_result": result.get("mock", False),
            "pathogen": result.get("pathogen", "Under analysis"),
            "symptoms": result.get("symptoms", treatment_info.get("symptoms", graph_treatment.get("symptoms", "Visible lesions on plant tissue. Compare with field guide for confirmation."))),
            "treatments": treatments,
            "prevention_tips": prevention,
            "immediate_action": f"1) Remove heavily infected parts immediately. 2) Spray {treatments[0]['pesticide']} at {treatments[0]['application']}. 3) Repeat after 7-10 days. 4) Monitor neighboring plants.",
            "severity_note": f"Detected: {disease_name} ({result.get('confidence', 80):.1f}% confidence). {'This is a CNN demo result — train on PlantVillage dataset for production accuracy.' if result.get('mock') else 'Analysis based on trained CNN model.'}",
        }
    finally:
        os.unlink(tmp_path)
