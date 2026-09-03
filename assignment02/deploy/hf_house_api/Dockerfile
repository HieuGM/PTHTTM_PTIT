# HF Space — FastAPI serving model + mobile page
FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py .
COPY house_pipeline.joblib ./model/house_pipeline.joblib
COPY mobile/index.html ./static/index.html

EXPOSE 7860
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "7860"]
