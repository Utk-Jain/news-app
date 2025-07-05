import logging

from fastapi import APIRouter, Query, HTTPException

from app.services.simulation import simulate_user_events

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("[simulate]")

router = APIRouter()


@router.post("/simulate")
def simulate_events(count: int = Query(500, description="Number of events to simulate")):
    try:
        result = simulate_user_events(count)
        return result

    except Exception as e:
        logger.error(f"Simulation failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Simulation failed: {str(e)}")