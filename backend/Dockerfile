FROM python:3.12-slim

WORKDIR /app

ENV PYTHONUNBUFFERED=1 \
    PYTHONUTF8=1

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 8000

# 数据库落在 /app/data，用卷持久化：docker run -v $PWD/data:/app/data ...
CMD ["uvicorn", "infopulse.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
