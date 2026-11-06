"""HTTP API and static demo. No patient identifiers or query persistence."""
from pathlib import Path
from contextlib import asynccontextmanager
import json
import math
import os
import csv
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse, JSONResponse
from fastapi.exceptions import RequestValidationError
from fastapi.staticfiles import StaticFiles
from app.agents.coordinator import Coordinator
from app.api_models import ChatRequest, PredictRequest, ReportRequest
from app.ml.schema import SCHEMAS
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env", override=False)
coordinator = None


@asynccontextmanager
async def lifespan(api):
    global coordinator
    coordinator = Coordinator(ROOT)
    from app.ml.predict import get_metadata
    for dataset in SCHEMAS:
        get_metadata(dataset)
    try:
        yield
    finally:
        coordinator.kb.close()


app = FastAPI(title="DiaCare Hybrid MAS", version="2.0.0", lifespan=lifespan)
app.mount("/static", StaticFiles(directory=ROOT / "app/static"), name="static")


@app.exception_handler(RequestValidationError)
async def validation_error(request, error):
    # Never echo raw health inputs; nonfinite JSON values also cannot be serialized.
    details = [{"loc": list(e["loc"]), "msg": e["msg"], "type": e["type"]}
               for e in error.errors()]
    if request.url.path == "/api/report" and coordinator is not None:
        from app.agents.contracts import Context
        context = Context("")
        context.emit("CoordinatorAgent", "started", {"workflow": "request-validation"},
                     version=coordinator.workflow.version)
        context.emit("PatientDataAgent", "invalid", {"error_code": "invalid_request"},
                     version=coordinator.workflow.data.version)
        result = coordinator.workflow._finish(context, "validation_error", error={
            "code": "invalid_request", "message": "Dữ liệu yêu cầu chưa hợp lệ.",
            "agent": "PatientDataAgent", "details": details})
        return JSONResponse(status_code=422, content=result)
    return JSONResponse(status_code=422, content={"detail": details})


@app.get("/")
def home():
    return FileResponse(ROOT / "app/static/index.html")


@app.get("/health")
def health():
    return {"status": "ok", "models": list(SCHEMAS), "kb": coordinator.kb.inventory(),
            "llm": coordinator.generator.configuration(), "system_version": "hybrid-mas-2.0"}


@app.get("/api/catalog")
def catalog():
    from app.ml.predict import get_metadata
    result = {}
    for name in SCHEMAS:
        metadata = get_metadata(name)
        result[name] = metadata
    return {"datasets": result, "knowledge": coordinator.kb.inventory(),
            "llm": coordinator.generator.configuration(), "core_agents": ["PatientDataAgent",
            "DLPredictionAgent", "RuleBasedAgent", "KGRAGAgent", "CoordinatorAgent",
            "ExplanationAgent", "MonitoringAgent"],
            "student": "Giáp Minh Hiếu", "student_id": "B23DCCN299"}


@app.get("/api/knowledge")
def knowledge():
    documents = [{k: doc.get(k) for k in ("id", "title", "url", "type", "ingestion",
                  "sha256", "page_count", "published_date", "updated_date")}
                 for doc in coordinator.kb.corpus["documents"]]
    return {"cards": coordinator.kb.cards, "documents": documents}


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


@app.post("/api/report")
def report(payload: ReportRequest):
    result = coordinator.report(payload.dataset, payload.features, payload.question,
                                payload.glucose, payload.unit)
    code = {"validation_error": 422, "dependency_error": 503}.get(result["status"], 200)
    return JSONResponse(status_code=code, content=result)


@app.get("/api/graph")
def graph():
    return coordinator.kb.graph_data()


@app.get("/api/benchmark")
def benchmark():
    folder = ROOT / "results/benchmark/full"
    summary = folder / "benchmark-results.json"
    if not summary.exists():
        return {"status": "not_available", "message": "Chưa có kết quả benchmark full."}
    result = json.loads(summary.read_text(encoding="utf-8"))
    with (folder / "summary.csv").open(encoding="utf-8-sig", newline="") as stream:
        result["summary"] = list(csv.DictReader(stream))
    return result


@app.get("/api/results")
def results():
    found = {}
    for file in sorted((ROOT / "results").glob("*.json")):
        if file.name in {"cdc-training.json", "hospital-training.json", "system-evaluation.json", "policy-training.json"}:
            found[file.stem] = json.loads(file.read_text(encoding="utf-8"))
    return found
