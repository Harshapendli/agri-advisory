from typing import Dict, List, Any, Optional
from graph.neo4j_client import neo4j_client

async def get_crop_subgraph(crop_name: str) -> Dict[str, Any]:
    records = await neo4j_client.run_query("""
        MATCH (c:Crop {name: $name})
        OPTIONAL MATCH (c)-[:GROWS_IN]->(s:Soil)
        OPTIONAL MATCH (c)-[:SUSCEPTIBLE_TO]->(d:Disease)
        OPTIONAL MATCH (c)-[:NEEDS]->(f:Fertilizer)
        RETURN c,
               collect(DISTINCT {soil: s.name, suitability: s.suitability}) as soils,
               collect(DISTINCT {disease: d.name, symptoms: d.symptoms, severity: d.severity}) as diseases,
               collect(DISTINCT {fertilizer: f.name, dose: f.application_rate_kg_per_hectare, timing: f.timing}) as fertilizers
    """, {"name": crop_name})
    if not records:
        return {}
    r = records[0]
    crop_props = dict(r["c"]) if r.get("c") else {}
    return {
        "crop": crop_props,
        "soils": [s for s in r.get("soils", []) if s.get("soil")],
        "diseases": [d for d in r.get("diseases", []) if d.get("disease")],
        "fertilizers": [f for f in r.get("fertilizers", []) if f.get("fertilizer")]
    }

async def get_diseases_for_crop(crop_name: str) -> List[Dict]:
    return await neo4j_client.run_query("""
        MATCH (c:Crop {name: $name})-[r:SUSCEPTIBLE_TO]->(d:Disease)
        OPTIONAL MATCH (d)-[:TREATED_BY]->(p:Pesticide)
        RETURN d.name as disease, d.symptoms as symptoms, d.pathogen_type as pathogen,
               r.severity as severity, collect(p.name) as treatments
    """, {"name": crop_name})

async def get_fertilizer_plan(crop_name: str, soil_type: str = None) -> List[Dict]:
    return await neo4j_client.run_query("""
        MATCH (c:Crop {name: $name})-[r:NEEDS]->(f:Fertilizer)
        RETURN f.name as fertilizer, r.dose_kg as dose_kg,
               r.timing as timing, f.N_content as N, f.P_content as P, f.K_content as K
        ORDER BY r.timing
    """, {"name": crop_name})

async def get_treatment_path(disease_name: str) -> Dict[str, Any]:
    records = await neo4j_client.run_query("""
        MATCH (d:Disease {name: $name})-[r:TREATED_BY]->(p:Pesticide)
        RETURN d.name as disease, d.symptoms as symptoms,
               collect({pesticide: p.name, application: r.application}) as treatments
    """, {"name": disease_name})
    return records[0] if records else {}

async def get_crops_for_soil(soil_type: str, season: str = None) -> List[Dict]:
    return await neo4j_client.run_query("""
        MATCH (c:Crop)-[r:GROWS_IN]->(s:Soil {name: $soil})
        WHERE $season IS NULL OR c.season = $season OR c.season = 'All'
        RETURN c.name as crop, c.season as season, c.water_req_mm as water_req,
               r.suitability as suitability
        ORDER BY CASE r.suitability WHEN 'high' THEN 1 WHEN 'medium' THEN 2 ELSE 3 END
    """, {"soil": soil_type, "season": season})

def subgraph_to_text(subgraph: Dict[str, Any]) -> str:
    if not subgraph:
        return ""
    parts = []
    crop = subgraph.get("crop", {})
    if crop:
        parts.append(f"CROP: {crop.get('name', 'Unknown')}")
        if crop.get("season"):
            parts.append(f"  Season: {crop['season']}")
        if crop.get("water_req_mm"):
            parts.append(f"  Water requirement: {crop['water_req_mm']} mm")
        if crop.get("yield_qtl_per_hectare"):
            parts.append(f"  Expected yield: {crop['yield_qtl_per_hectare']} qtl/hectare")
    soils = subgraph.get("soils", [])
    if soils:
        soil_names = [s["soil"] for s in soils if s.get("soil")]
        parts.append(f"SUITABLE SOILS: {', '.join(soil_names)}")
    diseases = subgraph.get("diseases", [])
    if diseases:
        parts.append("DISEASE RISKS:")
        for d in diseases[:3]:
            parts.append(f"  - {d.get('disease', '')}: {d.get('symptoms', '')} (severity: {d.get('severity', 'unknown')})")
    fertilizers = subgraph.get("fertilizers", [])
    if fertilizers:
        parts.append("FERTILIZER PLAN:")
        for f in fertilizers[:4]:
            parts.append(f"  - {f.get('fertilizer', '')}: {f.get('dose', '')} kg/ha at {f.get('timing', '')}")
    return "\n".join(parts)
