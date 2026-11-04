FROM node:22-slim AS interface
WORKDIR /build
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
WORKDIR /app
COPY requirements-verificado.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY api ./api
COPY app ./app
COPY data/exemplo ./data/exemplo
COPY --from=interface /build/dist ./frontend/dist
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
