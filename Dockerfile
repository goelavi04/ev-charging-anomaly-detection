# Stage 1 — build the React frontend
FROM node:20-slim AS frontend-builder
WORKDIR /app
COPY frontend/package*.json ./frontend/
RUN npm --prefix frontend ci
COPY frontend ./frontend
RUN npm --prefix frontend run build

# Stage 2 — Python backend + built frontend
FROM python:3.12-slim
WORKDIR /app

COPY backend/requirements.txt ./backend/requirements.txt
RUN pip install --no-cache-dir -r backend/requirements.txt

COPY backend ./backend
COPY ml ./ml
COPY --from=frontend-builder /app/frontend/dist ./frontend/dist

EXPOSE 10000
CMD uvicorn backend.main:app --host 0.0.0.0 --port ${PORT:-10000}
