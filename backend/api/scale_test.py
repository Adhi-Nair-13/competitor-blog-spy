from fastapi import APIRouter
from pydantic import BaseModel
from typing import Optional
from backend.services.scale_simulator import scale_simulator

router = APIRouter(prefix="/scale-test", tags=["Scale Test"])

class ScaleTestStartRequest(BaseModel):
    total_targets: int = 100
    concurrent_workers: int = 15

@router.post("/start")
async def start_scale_test(payload: Optional[ScaleTestStartRequest] = None):
    targets = payload.total_targets if payload else 100
    workers = payload.concurrent_workers if payload else 15
    res = await scale_simulator.start_simulation(total_targets=targets, workers=workers)
    return res

@router.get("/status")
def get_scale_test_status():
    return scale_simulator.get_status()
