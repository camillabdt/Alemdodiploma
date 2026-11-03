FROM node:22-slim AS interface
WORKDIR /build
COPY alumni-view-source.tar.gz SHA256SUMS ./
RUN sha256sum -c SHA256SUMS && tar -xzf alumni-view-source.tar.gz --strip-components=1 && rm alumni-view-source.tar.gz
RUN npm --prefix frontend ci && npm --prefix frontend run build

FROM python:3.12-slim
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1 PIP_NO_CACHE_DIR=1 OMP_NUM_THREADS=1 OPENBLAS_NUM_THREADS=1
WORKDIR /app
COPY --from=interface /build/requirements-verificado.txt ./requirements.txt
RUN pip install -r requirements.txt
COPY --from=interface /build/api ./api
COPY --from=interface /build/app ./app
COPY --from=interface /build/data/exemplo ./data/exemplo
COPY --from=interface /build/frontend/dist ./frontend/dist
EXPOSE 8000
CMD ["python", "-m", "uvicorn", "api.main:app", "--host", "0.0.0.0", "--port", "8000"]
