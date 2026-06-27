# Creative Trafficking API

REST API for ad creative lifecycle management across programmatic channels. Supports banner, video (VAST 2.0/3.0/4.x, VPAID), and native ad formats with built-in validation and trafficking workflows.

## Features

- **Creative CRUD** — create, retrieve, update status, and archive creatives
- **VAST/VPAID Validation** — validate VAST XML inline or fetch & validate a live tag URL
- **IAB Size Enforcement** — banner creatives validated against standard IAB ad sizes
- **Native Ad Compliance** — title/description length enforcement per IAB native spec
- **Impression & Click Tracking** — attach 3rd-party tracker URLs to any creative
- **Status Workflow** — `pending → active → paused → archived` with review notes

## Quickstart

```bash
python -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

API docs: http://localhost:8000/docs

## Docker

```bash
docker compose up
```

## API Reference

### Creatives

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/creatives/` | Create a banner, video, or native creative |
| `GET` | `/v1/creatives/` | List creatives (filter by advertiser, status, type) |
| `GET` | `/v1/creatives/{id}` | Get a single creative |
| `PATCH` | `/v1/creatives/{id}/status` | Update creative status |
| `DELETE` | `/v1/creatives/{id}` | Delete a creative |

### Validation

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/v1/validate/vast/xml` | Validate VAST XML string |
| `POST` | `/v1/validate/vast/tag` | Fetch and validate a VAST tag URL |

## Example: Create a Video Creative

```json
POST /v1/creatives/
{
  "name": "Q3 Awareness - 30s Pre-roll",
  "advertiser_id": "adv_abc123",
  "campaign_id": "cmp_xyz789",
  "creative_type": "video",
  "duration_seconds": 30,
  "skippable": true,
  "skip_offset_seconds": 5,
  "vast_tag_url": "https://ad.example.com/vast?id=12345",
  "click_url": "https://www.example.com/landing"
}
```

## Example: Validate VAST XML

```json
POST /v1/validate/vast/xml
{
  "xml": "<VAST version=\"3.0\">...</VAST>"
}
```

Response:
```json
{
  "valid": true,
  "version": "3.0",
  "errors": [],
  "warnings": ["Missing recommended tracking events: ['firstQuartile']"],
  "ad_title": "My Campaign Ad",
  "duration_seconds": 30,
  "media_file_count": 2,
  "tracking_events": ["complete", "midpoint", "start", "thirdQuartile"]
}
```

## Running Tests

```bash
pytest tests/ -v
```

## Tech Stack

- **FastAPI** — async REST framework
- **Pydantic v2** — request/response validation
- **httpx** — async HTTP for VAST tag fetching
- Python 3.12+
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27
<!-- Last updated: 2026-06-27 -->
