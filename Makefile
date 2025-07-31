# GCP configuration variables
GCP_PROJECT = talent-hunter-agent
GCP_REGION = australia-southeast2
ARTIFACT_REPO = talent-hunter-images
IMAGE_TAG = latest
DOCKER_BUILDKIT = 1

# Full image path
BACKEND_IMAGE = $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(ARTIFACT_REPO)/backend:$(IMAGE_TAG)
FRONTEND_IMAGE = $(GCP_REGION)-docker.pkg.dev/$(GCP_PROJECT)/$(ARTIFACT_REPO)/frontend:$(IMAGE_TAG)

build-backend:
	docker build -f Dockerfile.fastapi -t tha-backend .

build-backend-multistage:
	docker build -f Dockerfile.fastapi-multistage -t tha-backend .

build-frontend:
	docker build -f Dockerfile.streamlit -t tha-frontend .

build-all: build-backend build-frontend

# Build backend for GKE (linux/amd64)
build-backend-gke:
	docker build --platform linux/amd64 -f Dockerfile.fastapi -t $(BACKEND_IMAGE) .

build-backend-gke-multistage:
	docker build \
		--platform linux/amd64 \
		--build-arg PIP_INDEX_URL=https://download.pytorch.org/whl/cpu \
		--build-arg PIP_EXTRA_INDEX_URL=https://pypi.org/simple/ \
		-f Dockerfile.fastapi-multistage \
		-t $(BACKEND_IMAGE) \
		.

# Build frontend for GKE (linux/amd64)  
build-frontend-gke:
	docker build --platform linux/amd64 -f Dockerfile.streamlit -t $(FRONTEND_IMAGE) .

# Push backend to Artifact Registry
push-backend:
	docker push $(BACKEND_IMAGE)

# Push frontend to Artifact Registry
push-frontend:
	docker push $(FRONTEND_IMAGE)

# Build and push backend
deploy-backend: build-backend-gke push-backend
	kubectl rollout restart deployment talent-hunter-agent

# Build and push frontend
deploy-frontend: build-frontend-gke push-frontend
	kubectl rollout restart deployment talent-hunter-frontend

# Build and push all images
build-all-gke: build-backend-gke build-frontend-gke

# Push all images
push-all: push-backend push-frontend

# Full deployment pipeline
deploy-all: build-all-gke push-all
	kubectl rollout restart deployment talent-hunter-agent
	kubectl rollout restart deployment talent-hunter-frontend

# Run backend locally
run-backend:
	docker run -d -p 8000:8000 tha-backend

# Run frontend locally
run-frontend:
	docker run -d -p 8501:8501 tha-frontend

# Run all services locally
run-all:
	docker compose -f docker-compose.yaml up -d --build

# Stop all services locally
stop-all:
	docker compose down