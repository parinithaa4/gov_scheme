from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import Base, engine
from routers import auth, schemes, chat
from routers import guided_chat  # ADD THIS LINE
import uvicorn

# Create tables
Base.metadata.create_all(bind=engine)

# Create FastAPI app
app = FastAPI(
    title="Government Schemes API",
    description="Check eligibility for government schemes using AI",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth.router, prefix="/api/auth", tags=["Authentication"])
app.include_router(schemes.router, prefix="/api/schemes", tags=["Schemes"])
app.include_router(chat.router, prefix="/api/chat", tags=["Chat"])
app.include_router(guided_chat.router, prefix="/api/guided-chat", tags=["Guided Chat"])  # ADD THIS LINE

@app.get("/api/health")
def health_check():
    return {"status": "OK", "message": "Server is running"}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)