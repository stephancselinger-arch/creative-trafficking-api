from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
from typing import Optional

from app.services.vast_validator import validate_vast_xml, validate_vast_tag_url, ValidationResult

router = APIRouter(prefix="/validate", tags=["Validation"])


class VASTXMLRequest(BaseModel):
    xml: str


class VASTTagRequest(BaseModel):
    tag_url: HttpUrl
    timeout_seconds: int = 10


@router.post("/vast/xml", response_model=ValidationResult)
def validate_vast_xml_endpoint(body: VASTXMLRequest) -> ValidationResult:
    return validate_vast_xml(body.xml)


@router.post("/vast/tag", response_model=ValidationResult)
async def validate_vast_tag_endpoint(body: VASTTagRequest) -> ValidationResult:
    return await validate_vast_tag_url(str(body.tag_url), timeout=body.timeout_seconds)
