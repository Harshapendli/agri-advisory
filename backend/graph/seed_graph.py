import asyncio
from neo4j import AsyncGraphDatabase
from config import settings

CROPS = [
    {"name": "Rice", "season": "Kharif", "water_req_mm": 1200, "min_temp": 20, "max_temp": 35, "yield_qtl_per_hectare": 40},
    {"name": "Wheat", "season": "Rabi", "water_req_mm": 450, "min_temp": 10, "max_temp": 25, "yield_qtl_per_hectare": 45},
    {"name": "Maize", "season": "Kharif", "water_req_mm": 500, "min_temp": 18, "max_temp": 32, "yield_qtl_per_hectare": 35},
    {"name": "Cotton", "season": "Kharif", "water_req_mm": 700, "min_temp": 20, "max_temp": 38, "yield_qtl_per_hectare": 20},
    {"name": "Sugarcane", "season": "All", "water_req_mm": 1500, "min_temp": 20, "max_temp": 35, "yield_qtl_per_hectare": 700},
    {"name": "Tomato", "season": "Rabi", "water_req_mm": 600, "min_temp": 15, "max_temp": 30, "yield_qtl_per_hectare": 250},
    {"name": "Potato", "season": "Rabi", "water_req_mm": 500, "min_temp": 10, "max_temp": 20, "yield_qtl_per_hectare": 200},
    {"name": "Onion", "season": "Rabi", "water_req_mm": 350, "min_temp": 13, "max_temp": 28, "yield_qtl_per_hectare": 150},
    {"name": "Chickpea", "season": "Rabi", "water_req_mm": 300, "min_temp": 10, "max_temp": 25, "yield_qtl_per_hectare": 18},
    {"name": "Lentil", "season": "Rabi", "water_req_mm": 250, "min_temp": 8, "max_temp": 25, "yield_qtl_per_hectare": 15},
    {"name": "Mungbean", "season": "Kharif", "water_req_mm": 350, "min_temp": 25, "max_temp": 35, "yield_qtl_per_hectare": 10},
    {"name": "Blackgram", "season": "Kharif", "water_req_mm": 400, "min_temp": 25, "max_temp": 35, "yield_qtl_per_hectare": 12},
    {"name": "Banana", "season": "All", "water_req_mm": 1200, "min_temp": 20, "max_temp": 35, "yield_qtl_per_hectare": 300},
    {"name": "Mango", "season": "Kharif", "water_req_mm": 900, "min_temp": 24, "max_temp": 40, "yield_qtl_per_hectare": 100},
    {"name": "Grapes", "season": "Rabi", "water_req_mm": 700, "min_temp": 15, "max_temp": 35, "yield_qtl_per_hectare": 150},
    {"name": "Watermelon", "season": "Kharif", "water_req_mm": 400, "min_temp": 22, "max_temp": 35, "yield_qtl_per_hectare": 200},
    {"name": "Coconut", "season": "All", "water_req_mm": 1500, "min_temp": 27, "max_temp": 35, "yield_qtl_per_hectare": 80},
    {"name": "Jute", "season": "Kharif", "water_req_mm": 1000, "min_temp": 24, "max_temp": 37, "yield_qtl_per_hectare": 25},
    {"name": "Pigeonpeas", "season": "Kharif", "water_req_mm": 400, "min_temp": 20, "max_temp": 35, "yield_qtl_per_hectare": 15},
    {"name": "Mothbeans", "season": "Kharif", "water_req_mm": 200, "min_temp": 25, "max_temp": 40, "yield_qtl_per_hectare": 8},
    {"name": "Kidneybeans", "season": "Rabi", "water_req_mm": 350, "min_temp": 15, "max_temp": 28, "yield_qtl_per_hectare": 20},
    {"name": "Papaya", "season": "All", "water_req_mm": 1000, "min_temp": 22, "max_temp": 35, "yield_qtl_per_hectare": 400},
]

SOILS = [
    {"name": "Loamy", "pH_min": 6.0, "pH_max": 7.5, "water_retention": "high", "nutrients_level": "high"},
    {"name": "Sandy", "pH_min": 5.5, "pH_max": 7.0, "water_retention": "low", "nutrients_level": "low"},
    {"name": "Clay", "pH_min": 5.5, "pH_max": 7.5, "water_retention": "very_high", "nutrients_level": "medium"},
    {"name": "Black", "pH_min": 7.0, "pH_max": 8.5, "water_retention": "very_high", "nutrients_level": "high"},
    {"name": "Red", "pH_min": 5.5, "pH_max": 7.0, "water_retention": "medium", "nutrients_level": "low"},
    {"name": "Alluvial", "pH_min": 6.5, "pH_max": 7.5, "water_retention": "high", "nutrients_level": "very_high"},
]

DISEASES = [
    {"name": "Leaf Blight", "pathogen_type": "fungal", "symptoms": "Brown lesions on leaves, wilting", "affected_stage": "vegetative"},
    {"name": "Rust", "pathogen_type": "fungal", "symptoms": "Orange-red pustules on leaves", "affected_stage": "reproductive"},
    {"name": "Powdery Mildew", "pathogen_type": "fungal", "symptoms": "White powdery coating on leaves", "affected_stage": "vegetative"},
    {"name": "Root Rot", "pathogen_type": "fungal", "symptoms": "Yellowing, wilting, root decay", "affected_stage": "all"},
    {"name": "Bacterial Wilt", "pathogen_type": "bacterial", "symptoms": "Sudden wilting, vascular discoloration", "affected_stage": "vegetative"},
    {"name": "Mosaic Virus", "pathogen_type": "viral", "symptoms": "Mottled yellow-green leaves, stunted growth", "affected_stage": "all"},
    {"name": "Early Blight", "pathogen_type": "fungal", "symptoms": "Brown concentric rings on leaves", "affected_stage": "vegetative"},
    {"name": "Late Blight", "pathogen_type": "fungal", "symptoms": "Dark water-soaked lesions, white mold", "affected_stage": "reproductive"},
    {"name": "Anthracnose", "pathogen_type": "fungal", "symptoms": "Dark sunken spots on fruits and stems", "affected_stage": "reproductive"},
    {"name": "Cercospora", "pathogen_type": "fungal", "symptoms": "Small circular spots with dark borders", "affected_stage": "vegetative"},
]

FERTILIZERS = [
    {"name": "Urea", "N_content": 46, "P_content": 0, "K_content": 0, "application_rate_kg_per_hectare": 120},
    {"name": "DAP", "N_content": 18, "P_content": 46, "K_content": 0, "application_rate_kg_per_hectare": 100},
    {"name": "MOP", "N_content": 0, "P_content": 0, "K_content": 60, "application_rate_kg_per_hectare": 80},
    {"name": "NPK_17_17_17", "N_content": 17, "P_content": 17, "K_content": 17, "application_rate_kg_per_hectare": 200},
    {"name": "SSP", "N_content": 0, "P_content": 16, "K_content": 0, "application_rate_kg_per_hectare": 150},
    {"name": "Ammonium_Sulphate", "N_content": 21, "P_content": 0, "K_content": 0, "application_rate_kg_per_hectare": 100},
    {"name": "Zinc_Sulphate", "N_content": 0, "P_content": 0, "K_content": 0, "application_rate_kg_per_hectare": 25},
    {"name": "Borax", "N_content": 0, "P_content": 0, "K_content": 0, "application_rate_kg_per_hectare": 10},
]

PESTICIDES = [
    {"name": "Mancozeb", "type": "fungicide"},
    {"name": "Carbendazim", "type": "fungicide"},
    {"name": "Chlorpyrifos", "type": "insecticide"},
    {"name": "Imidacloprid", "type": "insecticide"},
    {"name": "Copper_Oxychloride", "type": "fungicide"},
    {"name": "Trichoderma", "type": "biocontrol"},
]

CROP_SOIL = [
    ("Rice", "Loamy", "high"), ("Rice", "Clay", "medium"), ("Rice", "Alluvial", "high"),
    ("Wheat", "Loamy", "high"), ("Wheat", "Alluvial", "high"), ("Wheat", "Clay", "medium"),
    ("Maize", "Sandy", "high"), ("Maize", "Loamy", "high"), ("Maize", "Red", "medium"),
    ("Cotton", "Black", "high"), ("Cotton", "Alluvial", "medium"), ("Cotton", "Red", "low"),
    ("Sugarcane", "Loamy", "high"), ("Sugarcane", "Alluvial", "high"), ("Sugarcane", "Black", "medium"),
    ("Tomato", "Loamy", "high"), ("Tomato", "Sandy", "medium"), ("Tomato", "Red", "medium"),
    ("Potato", "Sandy", "high"), ("Potato", "Loamy", "medium"), ("Potato", "Alluvial", "high"),
    ("Chickpea", "Black", "high"), ("Chickpea", "Loamy", "high"), ("Chickpea", "Sandy", "medium"),
    ("Mango", "Alluvial", "high"), ("Mango", "Red", "medium"), ("Mango", "Loamy", "high"),
    ("Banana", "Alluvial", "high"), ("Banana", "Loamy", "high"), ("Coconut", "Sandy", "high"),
    ("Grapes", "Black", "high"), ("Grapes", "Sandy", "medium"), ("Jute", "Alluvial", "high"),
    ("Pigeonpeas", "Black", "high"), ("Blackgram", "Loamy", "high"), ("Mungbean", "Sandy", "high"),
    ("Lentil", "Loamy", "high"), ("Kidneybeans", "Loamy", "high"), ("Onion", "Loamy", "high"),
]

CROP_DISEASE = [
    ("Rice", "Leaf Blight", "high"), ("Rice", "Bacterial Wilt", "medium"), ("Rice", "Cercospora", "medium"),
    ("Wheat", "Rust", "high"), ("Wheat", "Powdery Mildew", "medium"), ("Wheat", "Leaf Blight", "low"),
    ("Maize", "Leaf Blight", "medium"), ("Maize", "Rust", "medium"), ("Maize", "Mosaic Virus", "low"),
    ("Cotton", "Leaf Blight", "high"), ("Cotton", "Bacterial Wilt", "high"), ("Cotton", "Root Rot", "medium"),
    ("Tomato", "Early Blight", "high"), ("Tomato", "Late Blight", "high"), ("Tomato", "Mosaic Virus", "medium"),
    ("Potato", "Late Blight", "high"), ("Potato", "Early Blight", "medium"), ("Potato", "Root Rot", "medium"),
    ("Mango", "Anthracnose", "high"), ("Mango", "Powdery Mildew", "medium"),
    ("Grapes", "Powdery Mildew", "high"), ("Grapes", "Anthracnose", "medium"),
    ("Banana", "Leaf Blight", "medium"), ("Sugarcane", "Root Rot", "low"),
]

CROP_FERTILIZER = [
    ("Rice", "Urea", "basal", 120), ("Rice", "DAP", "basal", 60), ("Rice", "MOP", "top-dressing", 40),
    ("Wheat", "Urea", "basal", 100), ("Wheat", "DAP", "basal", 100), ("Wheat", "MOP", "basal", 40),
    ("Maize", "Urea", "basal", 120), ("Maize", "DAP", "basal", 60), ("Maize", "Zinc_Sulphate", "basal", 25),
    ("Cotton", "Urea", "basal", 80), ("Cotton", "DAP", "basal", 80), ("Cotton", "MOP", "top-dressing", 40),
    ("Tomato", "NPK_17_17_17", "basal", 200), ("Tomato", "Urea", "top-dressing", 50), ("Tomato", "Borax", "foliar", 10),
    ("Potato", "NPK_17_17_17", "basal", 250), ("Potato", "Urea", "top-dressing", 80), ("Potato", "MOP", "basal", 60),
    ("Sugarcane", "Urea", "basal", 150), ("Sugarcane", "SSP", "basal", 250), ("Sugarcane", "MOP", "basal", 60),
    ("Chickpea", "DAP", "basal", 50), ("Chickpea", "Zinc_Sulphate", "basal", 25),
    ("Mango", "Urea", "basal", 500), ("Mango", "SSP", "basal", 250),
    ("Banana", "Urea", "basal", 200), ("Banana", "MOP", "basal", 200),
]

DISEASE_TREATMENT = [
    ("Leaf Blight", "Mancozeb", "foliar spray"), ("Leaf Blight", "Copper_Oxychloride", "foliar spray"),
    ("Rust", "Mancozeb", "foliar spray"), ("Rust", "Carbendazim", "foliar spray"),
    ("Powdery Mildew", "Carbendazim", "foliar spray"), ("Powdery Mildew", "Copper_Oxychloride", "foliar spray"),
    ("Root Rot", "Trichoderma", "soil drench"), ("Root Rot", "Carbendazim", "soil drench"),
    ("Bacterial Wilt", "Copper_Oxychloride", "soil drench"),
    ("Mosaic Virus", "Imidacloprid", "foliar spray"),
    ("Early Blight", "Mancozeb", "foliar spray"), ("Early Blight", "Carbendazim", "foliar spray"),
    ("Late Blight", "Mancozeb", "foliar spray"), ("Late Blight", "Copper_Oxychloride", "foliar spray"),
    ("Anthracnose", "Carbendazim", "foliar spray"), ("Anthracnose", "Mancozeb", "foliar spray"),
    ("Cercospora", "Carbendazim", "foliar spray"),
]

async def seed():
    driver = AsyncGraphDatabase.driver(
        settings.NEO4J_URI, auth=(settings.NEO4J_USER, settings.NEO4J_PASSWORD)
    )
    print("Connected to Neo4j. Seeding data...")
    async with driver.session() as s:
        await s.run("MATCH (n) DETACH DELETE n")
        print("Cleared existing data")
        for c in CROPS:
            await s.run("MERGE (c:Crop {name: $name}) SET c += $props", {"name": c["name"], "props": c})
        print(f"Created {len(CROPS)} crop nodes")
        for soil in SOILS:
            await s.run("MERGE (s:Soil {name: $name}) SET s += $props", {"name": soil["name"], "props": soil})
        print(f"Created {len(SOILS)} soil nodes")
        for d in DISEASES:
            await s.run("MERGE (d:Disease {name: $name}) SET d += $props", {"name": d["name"], "props": d})
        print(f"Created {len(DISEASES)} disease nodes")
        for f in FERTILIZERS:
            await s.run("MERGE (f:Fertilizer {name: $name}) SET f += $props", {"name": f["name"], "props": f})
        print(f"Created {len(FERTILIZERS)} fertilizer nodes")
        for p in PESTICIDES:
            await s.run("MERGE (p:Pesticide {name: $name}) SET p += $props", {"name": p["name"], "props": p})
        print(f"Created {len(PESTICIDES)} pesticide nodes")
        for crop, soil, suitability in CROP_SOIL:
            await s.run("""
                MATCH (c:Crop {name:$crop}), (s:Soil {name:$soil})
                MERGE (c)-[r:GROWS_IN]->(s) SET r.suitability = $suit
            """, {"crop": crop, "soil": soil, "suit": suitability})
        print(f"Created {len(CROP_SOIL)} crop-soil relationships")
        for crop, disease, severity in CROP_DISEASE:
            await s.run("""
                MATCH (c:Crop {name:$crop}), (d:Disease {name:$disease})
                MERGE (c)-[r:SUSCEPTIBLE_TO]->(d) SET r.severity = $severity
            """, {"crop": crop, "disease": disease, "severity": severity})
        print(f"Created {len(CROP_DISEASE)} crop-disease relationships")
        for crop, fert, timing, dose in CROP_FERTILIZER:
            await s.run("""
                MATCH (c:Crop {name:$crop}), (f:Fertilizer {name:$fert})
                MERGE (c)-[r:NEEDS]->(f) SET r.timing = $timing, r.dose_kg = $dose
            """, {"crop": crop, "fert": fert, "timing": timing, "dose": dose})
        print(f"Created {len(CROP_FERTILIZER)} crop-fertilizer relationships")
        for disease, pesticide, method in DISEASE_TREATMENT:
            await s.run("""
                MATCH (d:Disease {name:$disease}), (p:Pesticide {name:$pest})
                MERGE (d)-[r:TREATED_BY]->(p) SET r.application = $method
            """, {"disease": disease, "pest": pesticide, "method": method})
        print(f"Created {len(DISEASE_TREATMENT)} disease-treatment relationships")
    await driver.close()
    print("\nSeeding complete! Knowledge graph is ready.")

if __name__ == "__main__":
    asyncio.run(seed())
