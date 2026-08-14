from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile, os, base64, json
from graph.graph_queries import get_treatment_path
from config import settings

router = APIRouter(prefix="/disease", tags=["disease"])

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
    "Mosaic Virus": {
        "treatments": [
            {"pesticide": "Imidacloprid 17.8% SL", "application": "Spray 0.5ml/liter to control aphid vectors", "dosage": "100ml per acre"},
            {"pesticide": "Neem Oil 1500 PPM", "application": "Spray 3ml/liter every 10 days", "dosage": "600ml per acre"},
        ],
        "prevention_tips": [
            "Remove and destroy infected plants immediately — no cure exists for viruses",
            "Control aphids and whiteflies which spread the virus",
            "Use virus-free certified seeds and seedlings",
            "Wash hands and tools with soap between handling different plants",
            "Grow barrier crops around the field to block vector insects"
        ]
    },
    "Anthracnose": {
        "treatments": [
            {"pesticide": "Carbendazim 50% WP", "application": "Spray 1g/liter every 7 days", "dosage": "200g per acre"},
            {"pesticide": "Mancozeb 75% WP", "application": "Spray 2.5g/liter as preventive", "dosage": "500g per acre"},
        ],
        "prevention_tips": [
            "Avoid harvesting fruits during wet/rainy conditions",
            "Maintain proper spacing and prune for air circulation",
            "Remove and destroy fallen infected fruits",
            "Use hot water seed treatment (52°C for 30 min) before sowing",
            "Apply post-harvest fungicide dip for stored fruits"
        ]
    },
    "Root Rot": {
        "treatments": [
            {"pesticide": "Metalaxyl 35% WS", "application": "Seed treatment 3g/kg seed", "dosage": "As needed"},
            {"pesticide": "Trichoderma viride", "application": "Soil application 2.5kg/acre mixed with FYM", "dosage": "2.5kg per acre"},
            {"pesticide": "Carbendazim 50% WP", "application": "Soil drench 1g/liter around root zone", "dosage": "200g per acre"},
        ],
        "prevention_tips": [
            "Ensure excellent soil drainage — avoid waterlogged conditions",
            "Use raised beds in heavy clay soils",
            "Rotate crops with cereals (wheat, maize) for 2-3 seasons",
            "Add organic matter to improve soil structure and beneficial microbes",
            "Avoid overwatering — let soil dry between irrigations"
        ]
    },
}


async def analyze_with_vision(image_bytes: bytes) -> dict:
    """Use GPT-4o-mini vision to analyze leaf image for disease detection."""
    from openai import AsyncOpenAI

    client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
    b64 = base64.b64encode(image_bytes).decode("utf-8")

    response = await client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are an expert agricultural plant pathologist. Analyze the provided leaf/plant image and determine if it is healthy or diseased.\n\n"
                    "You MUST respond with ONLY valid JSON (no markdown, no code fences) in this exact format:\n"
                    '{"status": "healthy" or "diseased", "disease_name": "Name of disease or Healthy", "confidence": 0-100, "symptoms": "description of visible symptoms or why leaf looks healthy", "pathogen": "pathogen name or N/A for healthy"}\n\n'
                    "Known diseases to check for: Early Blight, Late Blight, Leaf Blight, Powdery Mildew, Bacterial Wilt, Mosaic Virus, Anthracnose, Root Rot, "
                    "Leaf Curl, Rust, Downy Mildew, Black Rot, Brown Spot, Bacterial Spot, Leaf Mold, Septoria Leaf Spot.\n\n"
                    "IMPORTANT: If the leaf appears green, vibrant, and shows NO signs of disease (no spots, no discoloration, no wilting, no lesions, no mold), "
                    "classify it as HEALTHY with high confidence. Do NOT force a disease diagnosis on healthy plants.\n\n"
                    "If the image is not a plant/leaf, respond with: {\"status\": \"error\", \"disease_name\": \"Not a plant image\", \"confidence\": 0, \"symptoms\": \"Please upload a clear image of a plant leaf\", \"pathogen\": \"N/A\"}"
                ),
            },
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": "Analyze this leaf/plant image for any disease. Is it healthy or diseased?"},
                    {"type": "image_url", "image_url": {"url": f"data:image/jpeg;base64,{b64}", "detail": "low"}},
                ],
            },
        ],
        max_tokens=300,
        temperature=0.1,
    )

    text = response.choices[0].message.content.strip()
    # Remove markdown fences if present
    if text.startswith("```"):
        text = text.split("\n", 1)[1] if "\n" in text else text[3:]
    if text.endswith("```"):
        text = text[:-3]
    if text.startswith("json"):
        text = text[4:]
    text = text.strip()

    try:
        return json.loads(text)
    except json.JSONDecodeError:
        return {
            "status": "diseased",
            "disease_name": "Unknown",
            "confidence": 50.0,
            "symptoms": "Could not parse analysis. Please try again with a clearer image.",
            "pathogen": "Unknown",
        }


@router.post("/predict")
async def predict_disease(file: UploadFile = File(...)):
    allowed = {"image/jpeg", "image/png", "image/webp", "image/jpg"}
    if file.content_type and file.content_type not in allowed:
        raise HTTPException(status_code=400, detail="Only image files allowed (jpeg, png, webp)")

    content = await file.read()

    try:
        # Use GPT-4o-mini vision for accurate analysis
        vision_result = await analyze_with_vision(content)
        disease_name = vision_result.get("disease_name", "Unknown")
        confidence = float(vision_result.get("confidence", 75))
        is_healthy = vision_result.get("status") == "healthy" or "healthy" in disease_name.lower()

        if is_healthy:
            return {
                "disease_name": "Healthy ✅",
                "confidence": confidence,
                "is_mock_result": False,
                "pathogen": "None — no disease detected",
                "symptoms": vision_result.get("symptoms", "The leaf appears healthy with no visible signs of disease. Good green coloration, no spots, lesions, or discoloration observed."),
                "treatments": [],
                "prevention_tips": [
                    "Continue regular crop monitoring every 3-4 days",
                    "Maintain balanced fertilization — avoid excess nitrogen",
                    "Ensure proper irrigation schedule based on crop stage",
                    "Keep field clean — remove weeds and crop debris",
                    "Apply preventive neem oil spray (3ml/liter) every 15 days",
                ],
                "immediate_action": "No action needed — your plant looks healthy! Continue regular care and monitoring.",
                "severity_note": f"Analysis: Healthy leaf ({confidence:.1f}% confidence). No disease detected. Keep up the good farming practices!",
            }

        # Check for non-plant image
        if vision_result.get("status") == "error":
            return {
                "disease_name": "Not a Plant Image",
                "confidence": 0,
                "is_mock_result": False,
                "pathogen": "N/A",
                "symptoms": vision_result.get("symptoms", "Please upload a clear photo of a plant leaf for disease analysis."),
                "treatments": [],
                "prevention_tips": [
                    "Take a close-up photo of the affected leaf",
                    "Use natural daylight for best results",
                    "Focus on the area showing symptoms",
                    "Include both healthy and affected parts if possible",
                ],
                "immediate_action": "Please upload a clear image of a plant leaf to get disease analysis.",
                "severity_note": "Could not analyze — the uploaded image does not appear to be a plant leaf.",
            }

        # Diseased — get treatment info
        # Try to match with our treatment database (fuzzy match)
        matched_treatment_key = None
        for key in TREATMENT_DB:
            if key.lower() in disease_name.lower() or disease_name.lower() in key.lower():
                matched_treatment_key = key
                break

        treatment_info = TREATMENT_DB.get(matched_treatment_key, {}) if matched_treatment_key else {}
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
            "confidence": confidence,
            "is_mock_result": False,
            "pathogen": vision_result.get("pathogen", "Under analysis"),
            "symptoms": vision_result.get("symptoms", treatment_info.get("symptoms", graph_treatment.get("symptoms", "Visible lesions on plant tissue. Compare with field guide for confirmation."))),
            "treatments": treatments,
            "prevention_tips": prevention,
            "immediate_action": f"1) Remove heavily infected parts immediately. 2) Spray {treatments[0]['pesticide']} at {treatments[0]['application']}. 3) Repeat after 7-10 days. 4) Monitor neighboring plants.",
            "severity_note": f"Detected: {disease_name} ({confidence:.1f}% confidence). Analysis powered by AI vision model.",
        }

    except Exception as e:
        print(f"Vision analysis error: {e}")
        raise HTTPException(status_code=500, detail=f"Disease analysis failed: {str(e)}")
