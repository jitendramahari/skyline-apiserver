"""Read-only deployment configuration for console panel visibility."""

from typing import Dict, Optional

from fastapi import APIRouter, Depends
from pydantic import BaseModel, StrictBool

from skyline_apiserver import schemas
from skyline_apiserver.api import deps
from skyline_apiserver.config import CONF

router = APIRouter()


class Features(BaseModel):
    features: Dict[str, Optional[StrictBool]]


@router.get("/features", response_model=Features)
async def list_features(
    profile: schemas.Profile = Depends(deps.get_profile_update_jwt),
) -> Features:
    values = CONF.config.get("features")
    return Features(features={} if values is None else values)
