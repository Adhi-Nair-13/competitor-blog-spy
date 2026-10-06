import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.config import settings
from backend.database import engine, Base
from backend.api import api_router
from backend.services.monitoring_scheduler import monitoring_scheduler

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: initialize database tables
    logger.info("Initializing database tables...")
    Base.metadata.create_all(bind=engine)
    
    # Start continuous background monitoring scheduler
    logger.info("Starting background monitoring scheduler...")
    monitoring_scheduler.start()
    
    yield
    
    # Shutdown
    logger.info("Shutting down background monitoring scheduler...")
    monitoring_scheduler.stop()

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# Enable CORS for frontend Vite development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include central API router under /api
app.include_router(api_router, prefix=settings.API_V1_PREFIX)

@app.get("/")
def root():
    return {
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
        "docs": "/docs",
        "api": "/api",
        "status": "ONLINE",
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("backend.main:app", host="127.0.0.1", port=8000, reload=True)
