from enum import Enum
from typing import Optional
from pydantic import BaseModel, HttpUrl, field_validator
import uuid
from datetime import datetime


class CreativeType(str, Enum):
    BANNER = "banner"
    VIDEO = "video"
    NATIVE = "native"
    AUDIO = "audio"


class CreativeStatus(str, Enum):
    PENDING = "pending"
    ACTIVE = "active"
    PAUSED = "paused"
    ARCHIVED = "archived"


class AdSize(BaseModel):
    width: int
    height: int

    def __str__(self) -> str:
        return f"{self.width}x{self.height}"


STANDARD_IAB_SIZES = {
    (300, 250), (728, 90), (160, 600), (300, 600),
    (320, 50), (320, 480), (970, 250), (970, 90),
    (468, 60), (234, 60), (120, 600), (120, 240),
}


class CreativeBase(BaseModel):
    name: str
    advertiser_id: str
    campaign_id: Optional[str] = None
    creative_type: CreativeType
    click_url: Optional[HttpUrl] = None
    impression_tracker_urls: list[HttpUrl] = []
    click_tracker_urls: list[HttpUrl] = []


class BannerCreative(CreativeBase):
    creative_type: CreativeType = CreativeType.BANNER
    size: AdSize
    asset_url: HttpUrl
    backup_image_url: Optional[HttpUrl] = None
    is_html5: bool = False

    @field_validator("size")
    @classmethod
    def validate_iab_size(cls, v: AdSize) -> AdSize:
        if (v.width, v.height) not in STANDARD_IAB_SIZES:
            raise ValueError(
                f"{v.width}x{v.height} is not a standard IAB size. "
                f"Allowed: {sorted(STANDARD_IAB_SIZES)}"
            )
        return v


class VideoCreative(CreativeBase):
    creative_type: CreativeType = CreativeType.VIDEO
    vast_tag_url: Optional[HttpUrl] = None
    vast_xml: Optional[str] = None
    duration_seconds: int
    skippable: bool = False
    skip_offset_seconds: int = 5
    min_bitrate_kbps: int = 400
    max_bitrate_kbps: int = 1500
    protocols: list[int] = [2, 3, 5, 6]  # VAST 2.0, 3.0, VPAID 1.0, 2.0

    @field_validator("vast_tag_url", "vast_xml", mode="before")
    @classmethod
    def require_vast_source(cls, v, info):
        return v


class NativeCreative(CreativeBase):
    creative_type: CreativeType = CreativeType.NATIVE
    title: str
    description: str
    sponsored_by: str
    main_image_url: HttpUrl
    icon_url: Optional[HttpUrl] = None
    cta_text: str = "Learn More"

    @field_validator("title")
    @classmethod
    def title_length(cls, v: str) -> str:
        if len(v) > 90:
            raise ValueError("Native title must be <= 90 characters")
        return v

    @field_validator("description")
    @classmethod
    def description_length(cls, v: str) -> str:
        if len(v) > 140:
            raise ValueError("Native description must be <= 140 characters")
        return v


class CreativeRecord(BaseModel):
    id: str
    status: CreativeStatus = CreativeStatus.PENDING
    created_at: datetime
    updated_at: datetime
    review_notes: Optional[str] = None

    model_config = {"arbitrary_types_allowed": True}


class CreativeResponse(BaseModel):
    id: str
    name: str
    advertiser_id: str
    campaign_id: Optional[str]
    creative_type: CreativeType
    status: CreativeStatus
    created_at: datetime
    updated_at: datetime
    metadata: dict


def new_creative_id() -> str:
    return f"cr_{uuid.uuid4().hex[:16]}"
