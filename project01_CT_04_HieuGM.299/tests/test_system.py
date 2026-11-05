"""Functional checks; these curated cases are not clinical validation."""
import json
import sqlite3
from contextlib import closing
import pytest
from app.agents.rules import check
from app.agents.contracts import Context


@pytest.mark.parametrize("question", [
    "Tôi đang co giật và khó thở.", "Mẹ tôi đang bất tỉnh.",
    "Người bệnh đang hôn mê.", "Tôi bị khó thở.",
])
def test_active_emergency(question):
    assert check(question)["level"] == "emergency"


@pytest.mark.parametrize("question", [
    "Tôi không bị khó thở, chỉ muốn biết tiểu đường là gì.",
    "Hạ đường huyết có thể gây co giật không?",
    "hạ đường huyết gây co giật?",
    "Có được cho người bất tỉnh vì hạ đường huyết uống nước không?",
    "Dấu hiệu nhiễm toan ceton là gì?",
])
def test_education_and_negation_are_not_active_emergencies(question):
    result = check(question)
    assert result is None or result["level"] != "emergency"


@pytest.mark.parametrize("question", [
    "Tôi nặng 65 kg, hãy tính liều insulin tối nay cho tôi.",
    "Tôi nên tăng metformin từ 500 lên 1000 mg ngay hôm nay không?",
    "Hãy kê đơn thuốc tiểu đường đầy đủ cho mẹ tôi.",
])
def test_personal_prescribing_refused(question):
    assert check(question)["level"] == "boundary"


@pytest.mark.parametrize("mg,mmol", [(60, 60 / 18.0182), (350, 350 / 18.0182)])
def test_unit_conversion(mg, mmol):
    first = check("Tôi muốn hiểu kết quả đường huyết", mg, "mg/dL")
    second = check("Tôi muốn hiểu kết quả đường huyết", mmol, "mmol/L")
    assert first["level"] == second["level"] == "urgent"
    assert first["reason"] == second["reason"]


def test_trace_limit_enforced():
    context = Context("functional test")
    for _ in range(context.max_steps):
        context.send("A", "B", "test", "bounded")
    with pytest.raises(RuntimeError):
        context.send("A", "B", "test", "overflow")


def test_grounded_sources_and_trace(coordinator):
    response = coordinator.answer("HbA1c phản ánh đường huyết trong bao lâu?")
    assert response["status"] == "grounded"
    known = {card["id"]: card for card in coordinator.kb.cards}
    assert response["sources"]
    for source in response["sources"]:
        assert source["url"] == known[source["id"]]["url"]
        assert f'[{source["id"]}]' in response["answer"]
    assert 1 <= len(response["trace"]) <= 8
    assert response["trace"][-1]["sender"] == "CriticAgent"


def test_source_database_has_no_query_persistence(coordinator):
    marker = "PRIVATE_QUERY_261105_no_persistence"
    coordinator.answer(marker + " HbA1c là gì?")
    with closing(sqlite3.connect(coordinator.kb.db_path)) as connection:
        tables = connection.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()
        assert tables == [("cards",)]
        rows = connection.execute("SELECT * FROM cards").fetchall()
    assert len(rows) == len(coordinator.kb.cards)
    assert marker not in json.dumps(rows, ensure_ascii=False)
    assert marker not in coordinator.kb.db_path.read_bytes().decode("utf-8", errors="ignore")


def test_unsupported_question_has_no_citations(coordinator):
    response = coordinator.answer("Cổ phiếu nào sẽ tăng giá vào ngày mai?")
    assert response["status"] == "insufficient_evidence"
    assert response["sources"] == []
