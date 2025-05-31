from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import os

# Import API routes
from api.endpoints import api_router

# Create FastAPI app
app = FastAPI(
    title="Nell Beta 2",
    description="AI Writing Platform with modular workflows",
    version="1.0.0"
)

# CORS middleware for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],  # Vite dev server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router)

@app.get("/")
def root():
    return {
        "message": "Nell Beta 2 Backend",
        "status": "running", 
        "version": "1.0.0"
    }

@app.get("/health")
def health():
    return {"status": "healthy"}

@app.get("/projects")
def list_projects():
    # Your existing projects code...
    return {"projects": projects}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
