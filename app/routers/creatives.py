from typing import Annotated, Optional, Union
from fastapi import APIRouter, HTTPException, Query
from fastapi.responses import JSONResponse
from pydantic import ValidationError

from app.models.creative import (
    BannerCreative, VideoCreative, NativeCreative,
    CreativeResponse, CreativeStatus, CreativeType,
)
from app.services import creative_service

router = APIRouter(prefix="/creatives", tags=["Creatives"])


CreativePayload = Annotated[
    Union[BannerCreative, VideoCreative, NativeCreative],
    None,
]


@router.post("/", response_model=CreativeResponse, status_code=201)
async def create_creative(payload: Union[BannerCreative, VideoCreative, NativeCreative]):
    try:
        return await creative_service.create_creative(payload)
    except ValueError as e:
        raise HTTPException(status_code=422, detail=str(e))


@router.get("/", response_model=list[CreativeResponse])
def list_creatives(
    advertiser_id: Optional[str] = Query(None),
    status: Optional[CreativeStatus] = Query(None),
    creative_type: Optional[CreativeType] = Query(None),
    limit: int = Query(100, le=1000),
    offset: int = Query(0, ge=0),
):
    return creative_service.list_creatives(
        advertiser_id=advertiser_id,
        status=status,
        creative_type=creative_type,
        limit=limit,
        offset=offset,
    )


@router.get("/{creative_id}", response_model=CreativeResponse)
def get_creative(creative_id: str):
    creative = creative_service.get_creative(creative_id)
    if not creative:
        raise HTTPException(status_code=404, detail=f"Creative {creative_id} not found")
    return creative


@router.patch("/{creative_id}/status", response_model=CreativeResponse)
def update_status(creative_id: str, status: CreativeStatus, notes: Optional[str] = None):
    result = creative_service.update_creative_status(creative_id, status, notes)
    if not result:
        raise HTTPException(status_code=404, detail=f"Creative {creative_id} not found")
    return result


@router.delete("/{creative_id}", status_code=204)
def delete_creative(creative_id: str):
    if not creative_service.delete_creative(creative_id):
        raise HTTPException(status_code=404, detail=f"Creative {creative_id} not found")
