"""HTTP API and static demo. No patient identifiers or query persistence."""
from pathlib import Path
from contextlib import asynccontextmanager
import json
import math
import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ConfigDict, field_validator, StrictFloat, StrictInt
from app.agents.coordinator import Coordinator

ROOT = Path(__file__).resolve().parents[1]
coordinator = None


@asynccontextmanager
async def lifespan(api):
    global coordinator
    coordinator = Coordinator(ROOT)
    from app.ml.predict import get_metadata
    for dataset in ("cdc", "hospital"):
        get_metadata(dataset)
    yield


app = FastAPI(title="DiaCare MAS", version="1.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "app/static"), name="static")


@app.exception_handler(RequestValidationError)
async def validation_error(request, error):
    # Never echo raw health inputs; nonfinite JSON values also cannot be serialized.
    details = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
               for e in error.errors()]
    return JSONResponse(status_code=422, content={"detail": details})


class ChatRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    question: str = Field(min_length=3, max_length=2000)
    glucose: StrictFloat | StrictInt | None = Field(default=None, gt=0, le=1500)
    unit: str = Field(default="mg/dL", pattern=r"^(mg/dL|mmol/L)$")

    @field_validator("question")
    @classmethod
    def nonblank(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("Câu hỏi cần ít nhất 3 ký tự có nội dung.")
        return value.strip()

    @field_validator("glucose")
    @classmethod
    def finite(cls, value):
        if value is not None and not math.isfinite(value):
            raise ValueError("Giá trị phải hữu hạn.")
        return value


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset: str = Field(pattern="^(cdc|hospital)$")
    features: dict[str, StrictFloat | StrictInt]


@app.get("/")
def home():
    return FileResponse(ROOT / "app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok", "models": ["cdc", "hospital"], "kb": coordinator.kb.inventory()}


@app.get("/api/catalog")
def catalog():
    from app.ml.predict import get_metadata
    result = {}
    for name in ("cdc", "hospital"):
        metadata = get_metadata(name)
        result[name] = metadata
    return {"datasets": result, "knowledge": coordinator.kb.inventory(),
            "student": "Giáp Minh Hiếu", "student_id": "B23DCCN299"}


@app.get("/api/knowledge")
def knowledge():
    return {"cards": coordinator.kb.cards}


@app.post("/api/chat")
def chat(payload: ChatRequest):
    if payload.unit == "mmol/L" and payload.glucose is not None and payload.glucose > 83.3:
        raise HTTPException(422, "Giá trị mmol/L ngoài miền nhập cho phép.")
    return coordinator.answer(payload.question, payload.glucose, payload.unit)


@app.post("/api/predict")
def prediction(payload: PredictRequest):
    try:
        return coordinator.analyze(payload.dataset, payload.features)
    except (ValueError, TypeError, KeyError) as error:
        raise HTTPException(422, str(error)) from error


@app.get("/api/results")
def results():
    found = {}
    for file in sorted((ROOT / "results").glob("*.json")):
        if file.name in {"cdc-training.json", "hospital-training.json", "system-evaluation.json", "policy-training.json"}:
            found[file.stem] = json.loads(file.read_text(encoding="utf-8"))
    return found
