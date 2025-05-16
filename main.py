from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn

# from app.api.chat_route import router as chat_router
from app.api.test_chat_route import router as chat_router


# FastAPI App Initialization
app = FastAPI(
    title="PetPal",
    description="Virtual Pet Simulator.",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Routers
# app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])
app.include_router(chat_router, prefix="/api/v1", tags=["Chat"])

# Health Endpoints
@app.get("/")
async def root():
    
    return {"message": "Server is running"}

# Run the App
if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=1234, log_level="info")

