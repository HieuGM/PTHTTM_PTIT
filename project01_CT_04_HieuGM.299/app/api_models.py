"""Strict request schemas shared by legacy endpoints and the combined MAS report."""
import math
from pydantic import BaseModel, Field, ConfigDict, field_validator, StrictFloat, StrictInt
from app.ml.schema import SCHEMAS


class NumericRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    glucose: StrictFloat | StrictInt | None = Field(default=None, gt=0, le=1500)
    unit: str = Field(default="mg/dL", pattern=r"^(mg/dL|mmol/L)$")

    @field_validator("glucose")
    @classmethod
    def finite(cls, value):
        if value is not None and not math.isfinite(value):
            raise ValueError("Giá trị phải hữu hạn.")
        return value


class ChatRequest(NumericRequest):
    question: str = Field(min_length=3, max_length=2000)

    @field_validator("question")
    @classmethod
    def nonblank(cls, value):
        if len(value.strip()) < 3:
            raise ValueError("Câu hỏi cần ít nhất 3 ký tự có nội dung.")
        return value.strip()


class PredictRequest(BaseModel):
    model_config = ConfigDict(extra="forbid")
    dataset: str
    features: dict[str, StrictFloat | StrictInt]

    @field_validator("dataset")
    @classmethod
    def known_dataset(cls, value):
        if value not in SCHEMAS:
            raise ValueError("Bộ dữ liệu không hợp lệ.")
        return value


class ReportRequest(PredictRequest, NumericRequest):
    question: str = Field(default="", max_length=2000)

    @field_validator("question")
    @classmethod
    def trimmed(cls, value):
        return value.strip()
