import httpx
import json
from typing import Dict, Any, List, Optional
from langchain_core.messages import HumanMessage, SystemMessage
from graph.graph_queries import get_crop_subgraph, get_diseases_for_crop, get_fertilizer_plan, subgraph_to_text
from ml.predict_crop import predict_crop, FEATURE_NAMES
from ml.shap_explainer import get_shap_explanation
from config import settings

KNOWN_CROPS = [
    "rice", "wheat", "maize", "cotton", "sugarcane", "tomato", "potato", "onion",
    "chickpea", "lentil", "mungbean", "blackgram", "banana", "mango", "grapes",
    "watermelon", "coconut", "jute", "pigeonpeas", "mothbeans", "kidneybeans",
    "papaya", "paddy", "jowar", "bajra", "groundnut", "soybean", "sunflower",
    "mustard", "chilli", "turmeric", "ginger"
]

# Indian cities/districts for location extraction from queries
KNOWN_LOCATIONS = [
    "hyderabad", "warangal", "karimnagar", "nizamabad", "khammam", "nalgonda",
    "adilabad", "mahbubnagar", "medak", "rangareddy", "suryapet", "siddipet",
    "mancherial", "ramagundam", "godavarikhani", "jagitial", "peddapalli",
    "visakhapatnam", "vijayawada", "guntur", "nellore", "kurnool", "rajahmundry",
    "tirupati", "kakinada", "anantapur", "eluru", "kadapa", "ongole", "srikakulam",
    "bangalore", "mysore", "hubli", "dharwad", "belgaum", "mangalore", "gulbarga",
    "chennai", "coimbatore", "madurai", "salem", "tirupur", "erode", "vellore",
    "mumbai", "pune", "nagpur", "nashik", "aurangabad", "solapur", "kolhapur",
    "delhi", "lucknow", "kanpur", "varanasi", "agra", "jaipur", "jodhpur",
    "bhopal", "indore", "jabalpur", "gwalior", "ujjain", "raipur", "bilaspur",
    "kolkata", "patna", "ranchi", "bhubaneswar", "guwahati", "chandigarh",
    "ahmedabad", "surat", "rajkot", "vadodara", "thiruvananthapuram", "kochi",
    "telangana", "andhra pradesh", "karnataka", "tamil nadu", "maharashtra",
    "uttar pradesh", "madhya pradesh", "rajasthan", "gujarat", "kerala",
    "west bengal", "bihar", "odisha", "punjab", "haryana",
]

def extract_location(query: str, default: str = "Hyderabad") -> str:
    """Extract location/city/district name from the user's query."""
    q = query.lower()
    for loc in KNOWN_LOCATIONS:
        if loc in q:
            return loc.title()
    return default

KNOWN_DISEASES = [
    "leaf blight", "rust", "powdery mildew", "root rot", "bacterial wilt",
    "mosaic virus", "early blight", "late blight", "anthracnose", "cercospora",
    "leaf curl", "yellow spots", "brown spots", "fungal", "blight", "wilt",
    "mildew", "rot", "virus", "borer", "aphid", "whitefly"
]

LANGUAGE_NAMES = {
    "en": "English", "te": "Telugu", "hi": "Hindi", "mr": "Marathi", "kn": "Kannada"
}

def extract_entities(query: str) -> Dict[str, Optional[str]]:
    q = query.lower()
    found_crop = next((c for c in KNOWN_CROPS if c in q), None)
    found_disease = next((d for d in KNOWN_DISEASES if d in q), None)
    return {
        "crop": found_crop.title() if found_crop else None,
        "disease": found_disease.title() if found_disease else None
    }

async def fetch_weather(location: str) -> Dict[str, Any]:
    if not location or not settings.OPENWEATHER_API_KEY or settings.OPENWEATHER_API_KEY == "your_weather_key":
        return {"temp": 28, "humidity": 65, "description": "partly cloudy", "wind_speed": 12, "error": "No API key"}
    try:
        async with httpx.AsyncClient(timeout=5.0) as client:
            resp = await client.get(
                "https://api.openweathermap.org/data/2.5/weather",
                params={"q": location, "appid": settings.OPENWEATHER_API_KEY, "units": "metric"}
            )
            data = resp.json()
            if resp.status_code != 200:
                return {"temp": 28, "humidity": 65, "description": "data unavailable", "wind_speed": 10, "error": data.get("message", "API error")}
            return {
                "temp": data["main"]["temp"],
                "humidity": data["main"]["humidity"],
                "description": data["weather"][0]["description"],
                "wind_speed": data["wind"]["speed"],
                "feels_like": data["main"]["feels_like"],
                "error": None
            }
    except Exception as e:
        return {"temp": 28, "humidity": 65, "description": "data unavailable", "wind_speed": 10, "error": str(e)}

async def search_qdrant(query: str, limit: int = 3) -> List[str]:
    try:
        from rag.embeddings import EmbeddingModel
        from qdrant_client import AsyncQdrantClient
        client = AsyncQdrantClient(url=settings.QDRANT_URL, api_key=settings.QDRANT_API_KEY)
        embedding_model = EmbeddingModel()
        query_vector = embedding_model.encode(query)
        results = await client.search(collection_name="agri_knowledge", query_vector=query_vector, limit=limit)
        return [r.payload.get("text", "") for r in results if r.payload]
    except Exception:
        return []

def get_llm():
    """Get the LLM based on config - OpenAI or Gemini"""
    if settings.LLM_PROVIDER == "openai" and settings.OPENAI_API_KEY and settings.OPENAI_API_KEY != "your_openai_key":
        from langchain_openai import ChatOpenAI
        return ChatOpenAI(model="gpt-4o-mini", api_key=settings.OPENAI_API_KEY, temperature=0.3)
    elif settings.GEMINI_API_KEY and settings.GEMINI_API_KEY not in ("", "your_gemini_key"):
        from langchain_google_genai import ChatGoogleGenerativeAI
        return ChatGoogleGenerativeAI(model="gemini-1.5-flash", google_api_key=settings.GEMINI_API_KEY, temperature=0.3)
    else:
        return None

async def run_graphrag(
    query: str,
    soil_params: Optional[Dict[str, float]] = None,
    location: str = "Hyderabad",
    language: str = "en"
) -> Dict[str, Any]:
    entities = extract_entities(query)

    # Graph context
    graph_context = ""
    crop_name = entities["crop"]
    if not crop_name and soil_params:
        prediction = predict_crop(soil_params)
        crop_name = prediction.get("predicted_crop")
    if crop_name:
        subgraph = await get_crop_subgraph(crop_name)
        graph_context = subgraph_to_text(subgraph)

    # Vector search
    qdrant_docs = await search_qdrant(query)
    qdrant_context = "\n\n".join(qdrant_docs) if qdrant_docs else ""

    # Weather
    weather = await fetch_weather(location)

    # ML prediction
    ml_result = {}
    shap_factors = []
    if soil_params:
        ml_result = predict_crop(soil_params)
        shap_factors = get_shap_explanation(soil_params)

    # Build context strings
    weather_text = f"Current weather in {location}: {weather['temp']}°C, humidity {weather['humidity']}%, {weather['description']}, wind {weather['wind_speed']} km/h"

    soil_text = ""
    if soil_params:
        soil_text = f"Soil readings: N={soil_params.get('N')}, P={soil_params.get('P')}, K={soil_params.get('K')}, pH={soil_params.get('ph')}, Temperature={soil_params.get('temperature')}°C, Humidity={soil_params.get('humidity')}%, Rainfall={soil_params.get('rainfall')}mm"
        if ml_result.get("predicted_crop"):
            soil_text += f"\nML Model prediction: {ml_result['predicted_crop']} ({ml_result.get('confidence', 0):.1f}% confidence)"
            if shap_factors:
                top_factors = [f"{f['feature_label']}={f['value']} (importance: {f['shap_importance']:.3f})" for f in shap_factors[:3]]
                soil_text += f"\nKey factors: {', '.join(top_factors)}"

    lang_name = LANGUAGE_NAMES.get(language, "English")

    system_prompt = f"""You are KrishiMitra, an expert AI agricultural advisor for Indian farmers. You have deep knowledge of Indian farming practices, ICAR guidelines, soil science, crop management, and government agricultural schemes.

CRITICAL RULES:
- NEVER say "contact your local agricultural officer" or "consult an expert". YOU ARE the expert. Give direct, actionable advice.
- ALWAYS provide specific quantities, timings, and methods.
- ALWAYS include fertilizer dosage in kg/acre or kg/hectare.
- ALWAYS include irrigation schedules with specific frequencies.
- ALWAYS mention relevant government schemes with eligibility details.
- Tailor advice to the specific location and its climate conditions.
- If the query is in Telugu or Hindi, respond in that language.

You have access to:
1. Agricultural Knowledge Graph (Neo4j): crop-soil-disease-fertilizer relationships
2. Agricultural Research Documents (Qdrant): ICAR guidelines, best practices
3. Real-time Weather Data for the farmer's location
4. ML Model Predictions with SHAP explanations

Respond in {lang_name} language.

RESPOND AS VALID JSON with these exact fields:
{{
  "recommendation": "Main advisory text - 4-5 detailed sentences with specific actionable advice",
  "crop_advice": "Specific crop recommendation with scientific reasoning based on soil and weather",
  "fertilizer_plan": [
    {{"fertilizer": "name", "dose": "X kg/acre", "timing": "when exactly", "method": "how to apply"}}
  ],
  "irrigation_advice": "Specific irrigation schedule - frequency, method, quantity per acre",
  "disease_risk": [
    {{"disease": "name", "risk_level": "high/medium/low", "prevention": "specific preventive steps with product names and dosage"}}
  ],
  "weather_advisory": "How current weather in {location} specifically affects farming decisions today",
  "government_schemes": [
    {{"scheme": "scheme name", "benefit": "what farmer gets", "eligibility": "who can apply", "how_to_apply": "steps to apply"}}
  ],
  "irrigation_planning": {{
    "method": "recommended irrigation method",
    "frequency": "how often",
    "quantity": "liters per plant or mm per acre",
    "best_time": "morning/evening",
    "tips": "water conservation tips"
  }},
  "fertilizer_schedule": [
    {{"stage": "growth stage", "fertilizer": "name", "dose": "quantity", "timing": "days after sowing/planting"}}
  ],
  "pest_control": "Specific pest management advice with product names and dosage",
  "market_outlook": "Current market demand and price trends for recommended crops",
  "seasonal_tips": "Region-specific seasonal farming tips for {location}"
}}"""

    user_content = f"""Farmer's Query: {query}

Location: {location}
{soil_text if soil_text else "No soil data provided - give general advice for the region"}

Weather: {weather_text}

Knowledge Graph Context:
{graph_context if graph_context else "No specific crop data from knowledge graph"}

Agricultural Research Documents:
{qdrant_context if qdrant_context else "No additional research documents available"}

Provide comprehensive, specific farming advice. DO NOT suggest contacting anyone else - YOU provide the complete expert advice."""

    llm = get_llm()
    if llm:
        try:
            messages = [SystemMessage(content=system_prompt), HumanMessage(content=user_content)]
            response = await llm.ainvoke(messages)
            raw_text = response.content.strip()
            # Clean JSON from markdown
            if raw_text.startswith("```"):
                raw_text = raw_text.split("```")[1]
                if raw_text.startswith("json"):
                    raw_text = raw_text[4:]
                raw_text = raw_text.strip()
            if raw_text.endswith("```"):
                raw_text = raw_text[:-3].strip()
            try:
                advisory_json = json.loads(raw_text)
            except json.JSONDecodeError:
                advisory_json = _build_smart_fallback(query, entities, ml_result, weather, location, graph_context, language)
        except Exception as e:
            print(f"LLM error: {e}")
            advisory_json = _build_smart_fallback(query, entities, ml_result, weather, location, graph_context, language)
    else:
        advisory_json = _build_smart_fallback(query, entities, ml_result, weather, location, graph_context, language)

    return {
        "advisory": advisory_json,
        "shap_factors": shap_factors,
        "ml_prediction": ml_result,
        "weather": weather,
        "location": location,
        "language": language,
        "entities_detected": entities,
        "sources": ["Neo4j Knowledge Graph", "Qdrant Agricultural Docs", "OpenWeatherMap"] + (["XGBoost ML Model"] if soil_params else [])
    }


def _build_smart_fallback(query, entities, ml_result, weather, location, graph_context, language):
    """Build intelligent fallback when LLM is unavailable"""
    q = query.lower()
    crop = entities.get("crop") or (ml_result.get("predicted_crop") if ml_result else None) or "rice"
    temp = weather.get("temp", 28)
    humidity = weather.get("humidity", 65)

    # Fertilizer knowledge base
    fert_plans = {
        "rice": [
            {"fertilizer": "DAP", "dose": "50 kg/acre", "timing": "At transplanting (basal dose)", "method": "Broadcasting before final puddling"},
            {"fertilizer": "Urea", "dose": "35 kg/acre", "timing": "21 days after transplanting", "method": "Top dressing in standing water"},
            {"fertilizer": "Urea", "dose": "25 kg/acre", "timing": "45 days after transplanting (panicle initiation)", "method": "Top dressing"},
            {"fertilizer": "MOP", "dose": "20 kg/acre", "timing": "At transplanting", "method": "Basal application"},
        ],
        "wheat": [
            {"fertilizer": "DAP", "dose": "50 kg/acre", "timing": "At sowing", "method": "Drill with seed"},
            {"fertilizer": "Urea", "dose": "45 kg/acre", "timing": "21 days after sowing (first irrigation)", "method": "Broadcasting before irrigation"},
            {"fertilizer": "Urea", "dose": "25 kg/acre", "timing": "45 days after sowing", "method": "Top dressing"},
        ],
        "cotton": [
            {"fertilizer": "NPK 10:26:26", "dose": "50 kg/acre", "timing": "At sowing", "method": "Band placement"},
            {"fertilizer": "Urea", "dose": "35 kg/acre", "timing": "30 days after sowing", "method": "Ring application"},
            {"fertilizer": "Urea", "dose": "25 kg/acre", "timing": "60 days (square formation)", "method": "Side dressing"},
        ],
        "tomato": [
            {"fertilizer": "NPK 19:19:19", "dose": "5 kg/acre", "timing": "15 days after transplanting", "method": "Drip fertigation"},
            {"fertilizer": "Calcium Nitrate", "dose": "5 kg/acre", "timing": "30 days after transplanting", "method": "Drip fertigation"},
            {"fertilizer": "Urea", "dose": "20 kg/acre", "timing": "45 days after transplanting", "method": "Side dressing"},
        ],
    }

    irrigation_plans = {
        "rice": {"method": "Flood irrigation with AWD (Alternate Wetting and Drying)", "frequency": "Maintain 5cm standing water, drain every 7 days", "quantity": "1200-1500 mm per season", "best_time": "Morning 6-8 AM", "tips": "Use AWD method to save 25% water. Install field water tubes to monitor water level."},
        "wheat": {"method": "Border strip irrigation", "frequency": "Every 20-25 days, total 4-6 irrigations", "quantity": "40-50 mm per irrigation", "best_time": "Morning", "tips": "Critical irrigations at CRI stage (21 days), tillering, flowering, and grain filling."},
        "tomato": {"method": "Drip irrigation (recommended)", "frequency": "Every 2-3 days in summer, every 4-5 days in winter", "quantity": "2-3 liters per plant per day", "best_time": "Early morning 6-7 AM", "tips": "Use mulching to reduce water loss by 30%. Avoid overhead irrigation to prevent fungal diseases."},
        "cotton": {"method": "Furrow or drip irrigation", "frequency": "Every 10-15 days", "quantity": "50-60 mm per irrigation", "best_time": "Morning or evening", "tips": "Critical irrigation at flowering and boll formation stage. Stop irrigation 15 days before harvest."},
    }

    gov_schemes = [
        {"scheme": "PM-KISAN Samman Nidhi", "benefit": "Rs 6000/year in 3 installments directly to bank account", "eligibility": "All landholding farmer families", "how_to_apply": "Register at pmkisan.gov.in with Aadhaar and land records"},
        {"scheme": "PM Fasal Bima Yojana (PMFBY)", "benefit": "Crop insurance at 2% premium for Kharif, 1.5% for Rabi crops", "eligibility": "All farmers growing notified crops", "how_to_apply": "Apply through bank or CSC center before sowing deadline"},
        {"scheme": "Soil Health Card Scheme", "benefit": "Free soil testing + nutrient recommendations every 3 years", "eligibility": "All farmers", "how_to_apply": "Contact nearest Krishi Vigyan Kendra or apply at soilhealth.dac.gov.in"},
        {"scheme": "Per Drop More Crop (PDMC)", "benefit": "55% subsidy on micro-irrigation (drip/sprinkler) for small farmers", "eligibility": "All farmers, higher subsidy for SC/ST/small/marginal", "how_to_apply": "Apply at pmksy.gov.in or contact district agriculture office"},
    ]

    crop_lower = crop.lower() if crop else "rice"
    fert = fert_plans.get(crop_lower, fert_plans["rice"])
    irr = irrigation_plans.get(crop_lower, irrigation_plans["rice"])

    # Build disease risk based on weather
    disease_risks = []
    if humidity > 75:
        disease_risks.append({"disease": "Fungal infections (Leaf Blight, Powdery Mildew)", "risk_level": "high", "prevention": f"Apply Mancozeb 2.5g/liter as preventive spray every 10 days. Current humidity {humidity}% favors fungal growth."})
    if temp > 30:
        disease_risks.append({"disease": "Bacterial Wilt", "risk_level": "medium", "prevention": "Use Copper Oxychloride 3g/liter spray. Ensure proper drainage. Avoid waterlogging."})
    else:
        disease_risks.append({"disease": "Root Rot", "risk_level": "low", "prevention": "Apply Trichoderma viride 2kg/acre in soil. Maintain proper drainage."})

    recommendation = f"Based on your query about {query[:100]}, here is detailed advice for farming in {location}. "
    if ml_result and ml_result.get("predicted_crop"):
        recommendation += f"Your soil conditions are best suited for {ml_result['predicted_crop']} with {ml_result.get('confidence', 0):.1f}% confidence. "
    recommendation += f"Current weather in {location} shows {temp}°C and {humidity}% humidity which {'is favorable' if 20 < temp < 35 else 'needs attention'} for most crops. "
    recommendation += f"Follow the detailed fertilizer schedule and irrigation plan below for optimal yield."

    return {
        "recommendation": recommendation,
        "crop_advice": f"{crop} is recommended for your conditions in {location}. {'Kharif season crops like rice, maize, cotton are ideal now.' if 6 <= __import__('datetime').datetime.now().month <= 10 else 'Rabi season crops like wheat, chickpea, mustard are ideal now.'}" if crop else "Provide soil parameters for personalized crop recommendation.",
        "fertilizer_plan": fert,
        "irrigation_advice": f"Use {irr['method']}. Water {irr['frequency']}. Best time: {irr['best_time']}. {irr['tips']}",
        "disease_risk": disease_risks,
        "weather_advisory": f"Current {location} weather: {temp}°C, {humidity}% humidity, {weather.get('description', 'clear')}. {'High humidity increases fungal disease risk - apply preventive fungicide spray.' if humidity > 70 else 'Conditions are favorable for most farming operations.'}",
        "government_schemes": gov_schemes,
        "irrigation_planning": irr,
        "fertilizer_schedule": [
            {"stage": "Basal/Sowing", "fertilizer": fert[0]["fertilizer"], "dose": fert[0]["dose"], "timing": fert[0]["timing"]},
            {"stage": "Vegetative growth", "fertilizer": fert[1]["fertilizer"] if len(fert) > 1 else "Urea", "dose": fert[1]["dose"] if len(fert) > 1 else "30 kg/acre", "timing": fert[1]["timing"] if len(fert) > 1 else "3-4 weeks after sowing"},
        ],
        "pest_control": f"For {crop}: Apply Imidacloprid 0.5ml/liter for sucking pests (aphids, whiteflies). Use Chlorantraniliprole 0.3ml/liter for stem borers. Neem oil 3ml/liter as organic alternative every 7 days.",
        "market_outlook": f"Current market demand for {crop} is stable. Check local mandi prices at enam.gov.in before selling.",
        "seasonal_tips": f"In {location}: {'Apply mulching to conserve moisture in summer heat.' if temp > 30 else 'Ensure proper drainage during monsoon.' if humidity > 75 else 'Good conditions for field preparation and sowing.'}"
    }


async def run_chat_query(
    query: str,
    location: str = "Hyderabad",
    language: str = "en",
    history: List[Dict[str, str]] = []
) -> Dict[str, Any]:
    """Conversational chat — answers the user's actual question using OpenAI,
    weather data, and knowledge graph. No forced ML prediction."""

    # Extract location from the query itself (overrides default)
    detected_location = extract_location(query, default=location)

    # Extract crop/disease entities for knowledge graph lookup
    entities = extract_entities(query)

    # Fetch real weather for the detected location
    weather = await fetch_weather(detected_location)

    # Get knowledge graph context if a crop or disease is mentioned
    graph_context = ""
    if entities["crop"]:
        subgraph = await get_crop_subgraph(entities["crop"])
        graph_context = subgraph_to_text(subgraph)
    if entities["disease"]:
        # Try to get disease info for any crop
        try:
            diseases = await get_diseases_for_crop(entities.get("crop", ""))
            if diseases:
                graph_context += "\n\nDisease information:\n" + "\n".join(
                    [f"- {d.get('name', '')}: {d.get('symptoms', '')}" for d in diseases[:5]]
                )
        except Exception:
            pass

    # Vector search for additional context
    qdrant_docs = await search_qdrant(query)
    qdrant_context = "\n\n".join(qdrant_docs) if qdrant_docs else ""

    lang_name = LANGUAGE_NAMES.get(language, "English")
    weather_text = f"{detected_location}: {weather['temp']}°C, {weather['humidity']}% humidity, {weather['description']}"

    system_prompt = f"""You are KrishiMitra, an expert AI agricultural advisor for Indian farmers.
You are having a CONVERSATION with a farmer. Answer their specific question directly and naturally.

RULES:
- Answer the EXACT question the farmer asks. Don't give a generic dump.
- If they ask about a specific area/region, give advice specific to THAT region's climate, soil type, and common crops.
- If they ask "best crop for [area]", recommend 3-5 crops suited for that region with reasons.
- Be conversational, warm, and helpful — like talking to a knowledgeable friend.
- Give specific, actionable advice with quantities and timings.
- Keep responses focused — 2-4 paragraphs max unless they ask for detailed plans.
- Use the weather data to make advice current and relevant.
- Respond in {lang_name}.

You have access to:
- Real-time weather data for the farmer's area
- Agricultural Knowledge Graph with crop-soil-disease relationships
- Agricultural research documents"""

    # Build conversation history for context
    chat_messages = [SystemMessage(content=system_prompt)]
    for msg in history[-6:]:  # Keep last 6 messages for context
        if msg.get("role") == "user":
            chat_messages.append(HumanMessage(content=msg["text"]))
        elif msg.get("role") == "ai":
            from langchain_core.messages import AIMessage
            chat_messages.append(AIMessage(content=msg["text"]))

    user_content = f"""{query}

[Context — don't repeat this verbatim, use it to inform your answer]
Weather: {weather_text}
{f'Knowledge Graph: {graph_context}' if graph_context else ''}
{f'Research docs: {qdrant_context}' if qdrant_context else ''}"""

    chat_messages.append(HumanMessage(content=user_content))

    llm = get_llm()
    if llm:
        try:
            response = await llm.ainvoke(chat_messages)
            answer = response.content.strip()
        except Exception as e:
            print(f"Chat LLM error: {e}")
            answer = _build_chat_fallback(query, detected_location, weather, entities)
    else:
        answer = _build_chat_fallback(query, detected_location, weather, entities)

    return {
        "answer": answer,
        "location": detected_location,
        "weather": weather,
        "entities": entities,
        "sources": (["Neo4j Knowledge Graph"] if graph_context else [])
                 + (["Agricultural Research Docs"] if qdrant_context else [])
                 + ["OpenWeatherMap"]
    }


def _build_chat_fallback(query: str, location: str, weather: Dict, entities: Dict) -> str:
    """Simple fallback when LLM is unavailable for chat."""
    q = query.lower()
    temp = weather.get("temp", 28)
    humidity = weather.get("humidity", 65)

    # Region-based crop recommendations
    region_crops = {
        "warangal": "cotton, rice, maize, turmeric, and chilli",
        "karimnagar": "rice, cotton, maize, and soybean",
        "nizamabad": "rice, turmeric, soybean, and sugarcane",
        "hyderabad": "rice, maize, vegetables (tomato, onion), and flowers",
        "guntur": "cotton, chilli, tobacco, and rice",
        "vijayawada": "rice, sugarcane, mango, and banana",
        "bangalore": "ragi, vegetables, flowers, and fruits",
        "chennai": "rice, groundnut, sugarcane, and banana",
        "pune": "sugarcane, grapes, soybean, and onion",
        "nagpur": "cotton, soybean, oranges, and wheat",
    }

    loc_lower = location.lower()
    crops = region_crops.get(loc_lower, "rice, cotton, maize, and vegetables")

    if "best crop" in q or "which crop" in q or "what crop" in q:
        return (
            f"For {location} area, the best crops to grow are: {crops}. "
            f"Current weather ({temp}°C, {humidity}% humidity) is "
            f"{'favorable for kharif crops like rice and cotton' if humidity > 60 else 'suitable for rabi crops like wheat and chickpea'}. "
            f"Choose based on your soil type and available irrigation."
        )

    return (
        f"Based on current conditions in {location} ({temp}°C, {humidity}% humidity, {weather.get('description', '')}), "
        f"the commonly grown crops are {crops}. "
        f"For personalized advice, use the soil analysis feature with your soil test readings."
    )
