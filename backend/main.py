from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from beanie import init_beanie
from motor.motor_asyncio import AsyncIOMotorClient
from config import settings
from models.user import User
from models.farm import Farm
from models.soil import SoilReading
from models.advisory import Advisory, ChatMessage
from routers import auth, predict, advisory, disease, voice
from graph.neo4j_client import neo4j_client

@asynccontextmanager
async def lifespan(app: FastAPI):
    print("Starting AgriAdvisory API...")
    try:
        mongo_client = AsyncIOMotorClient(settings.MONGO_URI)
        db = mongo_client["agri_advisory"]
        await init_beanie(database=db, document_models=[User, Farm, SoilReading, Advisory, ChatMessage])
        print("MongoDB connected")
    except Exception as e:
        print(f"MongoDB connection failed: {e}")
    try:
        await neo4j_client.connect()
    except Exception as e:
        print(f"Neo4j connection failed: {e}")
    print("API ready!")
    yield
    await neo4j_client.close()
    print("API shutdown complete")

app = FastAPI(
    title="AgriAdvisory API",
    description="Knowledge Graph-Based Agricultural Advisory Recommendation Engine",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(predict.router)
app.include_router(advisory.router)
app.include_router(disease.router)
app.include_router(voice.router)

@app.get("/")
async def root():
    return {"message": "AgriAdvisory API running", "docs": "/docs", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {
        "status": "healthy",
        "services": {
            "api": "running",
            "mongodb": "connected",
            "neo4j": "connected" if neo4j_client._driver else "disconnected",
        }
    }
