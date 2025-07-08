build-backend:
	docker build -f Dockerfile.fastapi -t tha-backend .

build-frontend:
	docker build -f Dockerfile.streamlit -t tha-frontend .

build-all: build-backend build-frontend

run-backend:
	docker run -d -p 8000:8000 tha-backend

run-frontend:
	docker run -d -p 8501:8501 tha-frontend

run-all:
	docker compose -f docker-compose.yaml up -d

stop-all:
	docker compose down