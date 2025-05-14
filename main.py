from fastapi import FastAPI

from app.api.user_route import router as auth_router
from app.api.pet_profile_route import router as pet_router
from app.api.chat_route import router as chat_router

# FastAPI App Initialization
app = FastAPI(
    title="PetPal",
    description="Virtual Pet Simulator.",
    version="1.0.0",
)

# Routers
app.include_router(auth_router, prefix="/api/auth", tags=["User Creation"])
app.include_router(pet_router, prefix="/api/pet", tags=["Pet Profile"])
app.include_router(chat_router, prefix="/api", tags=["Chat"])

# Health Endpoints
@app.get("/")
async def root():
    
    return {"message": "Server is running"}

