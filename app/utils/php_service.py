import httpx

API_BASE = "http://43.201.147.104/aipet/api/v1"

async def get_user_by_id(user_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{API_BASE}/users/profile", headers=headers)
        response.raise_for_status()
        return response.json().get("user", {})

async def get_pet_by_id(pet_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(f"{API_BASE}/pets", headers=headers)
        response.raise_for_status()
        pets = response.json().get("pets", [])

    for pet in pets:
        if str(pet.get("pet_id")) == str(pet_id):
            return pet

    return None
