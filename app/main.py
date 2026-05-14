from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import creatives, validation

app = FastAPI(
    title="Creative Trafficking API",
    description=(
        "Ad creative lifecycle management — upload, validate, and traffic "
        "banner, video (VAST/VPAID), and native creatives across programmatic channels."
    ),
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(creatives.router, prefix="/v1")
app.include_router(validation.router, prefix="/v1")


@app.get("/health")
def health():
    return {"status": "ok"}
