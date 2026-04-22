from pathlib import Path

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi import Request

from .data import SAMPLE_SETS
from .schemas import CompareRequest, CompareResponse
from .services import compare_products


BASE_DIR = Path(__file__).resolve().parent.parent

app = FastAPI(
    title="BuyOrBye",
    description="Compare products by price, quality, and value.",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/static", StaticFiles(directory=BASE_DIR / "static"), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))


@app.get("/", response_class=HTMLResponse)
async def home(request: Request) -> HTMLResponse:
    return templates.TemplateResponse(
        "index.html",
        {
            "request": request,
            "sample_sets": SAMPLE_SETS,
        },
    )


@app.get("/api/health")
async def healthcheck() -> dict:
    return {"status": "ok"}


@app.get("/api/samples")
async def sample_sets() -> dict:
    return SAMPLE_SETS


@app.post("/api/compare", response_model=CompareResponse)
async def compare(payload: CompareRequest) -> CompareResponse:
    result = compare_products(
        raw_entries=payload.links,
        priority_mode=payload.priority_mode,
        category_mode=payload.category_mode,
    )
    return CompareResponse(**result)
