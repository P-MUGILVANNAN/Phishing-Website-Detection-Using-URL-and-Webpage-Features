from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database.models import init_db
from app.ml.predict import model_predictor
from app.core.logging_config import logger
from app.api import health, predict, datasets, training, evaluation, history

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup actions
    logger.info("Initializing PhishGuard AI backend system...")
    init_db()
    model_loaded = model_predictor.load_model()
    if model_loaded:
        logger.info("Model loaded successfully at startup.")
    else:
        logger.info("System started in clean UNTRAINED state.")
    yield
    # Shutdown actions
    logger.info("PhishGuard AI backend shutting down.")

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    description="Research-Oriented Phishing Detection System using XGBoost, NLP, and Domain-Disjoint Robustness Evaluation",
    lifespan=lifespan
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API Routers
app.include_router(health.router, prefix=settings.API_PREFIX, tags=["Health"])
app.include_router(predict.router, prefix=settings.API_PREFIX, tags=["Prediction"])
app.include_router(datasets.router, prefix=settings.API_PREFIX, tags=["Datasets"])
app.include_router(training.router, prefix=settings.API_PREFIX, tags=["Training"])
app.include_router(evaluation.router, prefix=settings.API_PREFIX, tags=["Evaluation"])
app.include_router(history.router, prefix=settings.API_PREFIX, tags=["History & Reports"])

@app.get("/")
def root():
    return {
        "service": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs_url": "/docs",
        "api_prefix": settings.API_PREFIX
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)

