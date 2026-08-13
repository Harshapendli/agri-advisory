import pytest
from fastapi.testclient import TestClient
import sys, os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

def test_root_endpoint():
    from main import app
    client = TestClient(app)
    resp = client.get("/")
    assert resp.status_code == 200
    assert "AgriAdvisory" in resp.json()["message"]

def test_entity_extraction():
    from rag.graphrag_chain import extract_entities
    result = extract_entities("What fertilizer should I use for rice?")
    assert result["crop"] == "Rice"

def test_entity_extraction_disease():
    from rag.graphrag_chain import extract_entities
    result = extract_entities("My wheat has rust disease")
    assert result["crop"] == "Wheat"
    assert result["disease"] == "Rust"

def test_predict_crop_no_model():
    from ml.predict_crop import predict_crop
    result = predict_crop({"N": 90, "P": 42, "K": 43, "temperature": 25, "humidity": 70, "ph": 6.5, "rainfall": 200})
    assert "predicted_crop" in result or "error" in result

def test_soil_input_validation():
    from routers.predict import SoilInput
    soil = SoilInput(N=90, P=42, K=43, temperature=25, humidity=70, ph=6.5, rainfall=200)
    assert soil.N == 90
    with pytest.raises(Exception):
        SoilInput(N=999, P=42, K=43, temperature=25, humidity=70, ph=6.5, rainfall=200)

def test_subgraph_to_text_empty():
    from graph.graph_queries import subgraph_to_text
    assert subgraph_to_text({}) == ""

def test_password_hashing():
    from models.user import User
    hashed = User.hash_password("test123")
    assert hashed != "test123"
