from datetime import datetime, timezone
from typing import Optional, Union
import uuid

from app.models.creative import (
    BannerCreative, VideoCreative, NativeCreative,
    CreativeResponse, CreativeStatus, CreativeType,
    new_creative_id,
)
from app.services.vast_validator import validate_vast_xml, validate_vast_tag_url


# In-memory store — swap for PostgreSQL / DynamoDB in production
_store: dict[str, dict] = {}


def _now() -> datetime:
    return datetime.now(timezone.utc)


def _build_response(record: dict) -> CreativeResponse:
    return CreativeResponse(
        id=record["id"],
        name=record["name"],
        advertiser_id=record["advertiser_id"],
        campaign_id=record.get("campaign_id"),
        creative_type=record["creative_type"],
        status=record["status"],
        created_at=record["created_at"],
        updated_at=record["updated_at"],
        metadata=record.get("metadata", {}),
    )


async def create_creative(
    creative: Union[BannerCreative, VideoCreative, NativeCreative]
) -> CreativeResponse:
    creative_id = new_creative_id()
    now = _now()

    metadata: dict = {}
    if isinstance(creative, BannerCreative):
        metadata = {"size": str(creative.size), "is_html5": creative.is_html5}
    elif isinstance(creative, VideoCreative):
        metadata = {
            "duration_seconds": creative.duration_seconds,
            "skippable": creative.skippable,
            "protocols": creative.protocols,
        }
        if creative.vast_xml:
            result = validate_vast_xml(creative.vast_xml)
            if not result.valid:
                raise ValueError(f"VAST validation failed: {result.errors}")
            metadata["vast_version"] = result.version
            metadata["tracking_events"] = result.tracking_events
        elif creative.vast_tag_url:
            result = await validate_vast_tag_url(str(creative.vast_tag_url))
            if not result.valid:
                raise ValueError(f"VAST tag validation failed: {result.errors}")
            metadata["vast_version"] = result.version
    elif isinstance(creative, NativeCreative):
        metadata = {
            "title_length": len(creative.title),
            "description_length": len(creative.description),
            "has_icon": creative.icon_url is not None,
        }

    record = {
        "id": creative_id,
        "name": creative.name,
        "advertiser_id": creative.advertiser_id,
        "campaign_id": creative.campaign_id,
        "creative_type": creative.creative_type,
        "status": CreativeStatus.PENDING,
        "created_at": now,
        "updated_at": now,
        "metadata": metadata,
        "raw": creative.model_dump(),
    }
    _store[creative_id] = record
    return _build_response(record)


def get_creative(creative_id: str) -> Optional[CreativeResponse]:
    record = _store.get(creative_id)
    if not record:
        return None
    return _build_response(record)


def list_creatives(
    advertiser_id: Optional[str] = None,
    status: Optional[CreativeStatus] = None,
    creative_type: Optional[CreativeType] = None,
    limit: int = 100,
    offset: int = 0,
) -> list[CreativeResponse]:
    results = list(_store.values())
    if advertiser_id:
        results = [r for r in results if r["advertiser_id"] == advertiser_id]
    if status:
        results = [r for r in results if r["status"] == status]
    if creative_type:
        results = [r for r in results if r["creative_type"] == creative_type]
    return [_build_response(r) for r in results[offset : offset + limit]]


def update_creative_status(creative_id: str, status: CreativeStatus, notes: Optional[str] = None) -> Optional[CreativeResponse]:
    record = _store.get(creative_id)
    if not record:
        return None
    record["status"] = status
    record["updated_at"] = _now()
    if notes:
        record["review_notes"] = notes
    return _build_response(record)


def delete_creative(creative_id: str) -> bool:
    if creative_id not in _store:
        return False
    _store.pop(creative_id)
    return True
