"""
VAST 2.0 / 3.0 / 4.x validator.
Validates structure, required nodes, media file presence, and tracking events.
"""

import xml.etree.ElementTree as ET
from dataclasses import dataclass, field
from typing import Optional
import httpx


VAST_NAMESPACES = {
    "2.0": "http://www.iab.net/vast",
    "3.0": "http://www.iab.net/vast",
}

REQUIRED_TRACKING_EVENTS = {"start", "firstQuartile", "midpoint", "thirdQuartile", "complete"}

VALID_MIME_TYPES = {
    "video/mp4", "video/webm", "video/ogg",
    "application/x-shockwave-flash",
    "application/javascript",  # VPAID
}


@dataclass
class ValidationResult:
    valid: bool
    version: Optional[str] = None
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    ad_title: Optional[str] = None
    duration_seconds: Optional[int] = None
    media_file_count: int = 0
    tracking_events: list[str] = field(default_factory=list)


def parse_duration(duration_str: str) -> Optional[int]:
    """Convert HH:MM:SS to total seconds."""
    try:
        parts = duration_str.strip().split(":")
        if len(parts) == 3:
            h, m, s = parts
            return int(h) * 3600 + int(m) * 60 + int(s)
    except (ValueError, AttributeError):
        pass
    return None


def validate_vast_xml(xml_string: str) -> ValidationResult:
    result = ValidationResult(valid=True)

    try:
        root = ET.fromstring(xml_string)
    except ET.ParseError as e:
        return ValidationResult(valid=False, errors=[f"XML parse error: {e}"])

    if root.tag != "VAST":
        result.valid = False
        result.errors.append(f"Root element must be <VAST>, got <{root.tag}>")
        return result

    version = root.get("version", "")
    result.version = version
    if not version.startswith(("2.", "3.", "4.")):
        result.warnings.append(f"Unrecognized VAST version: {version}")

    ad_el = root.find("Ad")
    if ad_el is None:
        result.valid = False
        result.errors.append("Missing required <Ad> element")
        return result

    inline = ad_el.find("InLine")
    wrapper = ad_el.find("Wrapper")

    if inline is None and wrapper is None:
        result.valid = False
        result.errors.append("<Ad> must contain either <InLine> or <Wrapper>")
        return result

    node = inline if inline is not None else wrapper

    ad_title = node.findtext("AdTitle")
    result.ad_title = ad_title
    if not ad_title:
        result.warnings.append("Missing <AdTitle> — recommended for reporting")

    if node.findtext("Impression") is None:
        result.errors.append("Missing required <Impression> tracking pixel")
        result.valid = False

    creatives = node.find("Creatives")
    if creatives is None:
        result.valid = False
        result.errors.append("Missing <Creatives> element")
        return result

    linear = creatives.find(".//Linear")
    if linear is not None:
        duration_str = linear.findtext("Duration")
        if not duration_str:
            result.errors.append("Missing <Duration> inside <Linear>")
            result.valid = False
        else:
            result.duration_seconds = parse_duration(duration_str)
            if result.duration_seconds is None:
                result.errors.append(f"Unparseable <Duration>: {duration_str}")
                result.valid = False

        media_files = linear.findall(".//MediaFile")
        result.media_file_count = len(media_files)
        if not media_files:
            result.errors.append("No <MediaFile> elements found")
            result.valid = False

        for mf in media_files:
            mime = mf.get("type", "")
            if mime and mime not in VALID_MIME_TYPES:
                result.warnings.append(f"Unusual MediaFile MIME type: {mime}")
            delivery = mf.get("delivery", "")
            if delivery not in ("progressive", "streaming", ""):
                result.warnings.append(f"Unexpected delivery attribute: {delivery}")

        found_events: set[str] = set()
        for event_el in linear.findall(".//Tracking"):
            event = event_el.get("event", "")
            if event:
                found_events.add(event)
        result.tracking_events = sorted(found_events)

        missing = REQUIRED_TRACKING_EVENTS - found_events
        if missing:
            result.warnings.append(
                f"Missing recommended tracking events: {sorted(missing)}"
            )

    return result


async def validate_vast_tag_url(url: str, timeout: int = 10) -> ValidationResult:
    """Fetch a VAST tag URL and validate the returned XML."""
    try:
        async with httpx.AsyncClient(follow_redirects=True, timeout=timeout) as client:
            resp = await client.get(url)
            resp.raise_for_status()
            return validate_vast_xml(resp.text)
    except httpx.TimeoutException:
        return ValidationResult(valid=False, errors=[f"Timeout fetching VAST tag after {timeout}s"])
    except httpx.HTTPStatusError as e:
        return ValidationResult(
            valid=False,
            errors=[f"HTTP {e.response.status_code} fetching VAST tag"]
        )
    except Exception as e:
        return ValidationResult(valid=False, errors=[str(e)])
