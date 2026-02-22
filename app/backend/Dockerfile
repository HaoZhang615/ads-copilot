FROM python:3.11-slim
WORKDIR /workspace

COPY app/backend/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY databricks-ads-session /workspace/databricks-ads-session
COPY app/backend /workspace/app/backend

ENV PYTHONPATH=/workspace

EXPOSE 8000

CMD ["uvicorn", "app.backend.main:app", "--host", "0.0.0.0", "--port", "8000"]
