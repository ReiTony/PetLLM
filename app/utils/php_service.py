import httpx
import logging

API_BASE = "http://54.180.147.58/aipet/api/v1"

logger = logging.getLogger(__name__)

async def get_user_by_id(user_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{API_BASE}/users/profile", headers=headers)
            response.raise_for_status()
            return response.json().get("user", {})
        except httpx.HTTPStatusError as e:
            logger.error("User API returned %s: %s", e.response.status_code, e)
            raise
        except httpx.RequestError as e:
            logger.error("User API request error: %s", e)
            raise

async def get_pet_by_id(pet_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{API_BASE}/pets/{pet_id}", headers=headers)
            if response.status_code == 404:
                logger.warning("Pet %s not found", pet_id)
                return None
            response.raise_for_status()
            return response.json().get("pet")
        except httpx.HTTPStatusError as e:
            logger.error("Pet API returned %s: %s", e.response.status_code, e)
            raise
        except httpx.RequestError as e:
            logger.error("Pet API request error: %s", e)
            raise

async def get_pet_status_by_id(pet_id: str, token: str):
    headers = {"Authorization": f"Bearer {token}"}
    async with httpx.AsyncClient(timeout=10.0) as client:
        try:
            response = await client.get(f"{API_BASE}/pets/{pet_id}/status", headers=headers)
            if response.status_code == 404:
                logger.warning("No status found for pet %s", pet_id)
                return {}
            response.raise_for_status()
            return response.json().get("data", {})
        except httpx.HTTPStatusError as e:
            logger.error("Pet status API returned %s: %s", e.response.status_code, e)
            raise
        except httpx.RequestError as e:
            logger.error("Pet status request error: %s", e)
            raise