from fastapi import FastAPI

app = FastAPI(
    title="CKM Nexus API",
    version="0.1.0",
    description="AI-powered Mining Intelligence Platform"
)

@app.get("/")
def root():
    return {
        "application": "CKM Nexus",
        "status": "running"
    }

@app.get("/health")
def health():
    return {
        "status": "healthy"
    }
