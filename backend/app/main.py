from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.database.base import Base
from app.database.session import engine
from app.api.health import router as health_router
from app.api.articles import router as articles_router
from app.api.websites import router as websites_router
from app.api.v1.websites import router as v1_websites_router
from app.api.v1.search import router as v1_search_router
from app.integrations.wordpress.endpoints import router as wordpress_router
from app.core.config import settings

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="African Mining Intelligence Platform"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(health_router)
app.include_router(articles_router)
app.include_router(websites_router)
app.include_router(v1_websites_router)
app.include_router(v1_search_router)
app.include_router(wordpress_router)

@app.get("/")
def root():
    return {
        "message": "Welcome to CKM Nexus",
        "version": settings.APP_VERSION
    }
