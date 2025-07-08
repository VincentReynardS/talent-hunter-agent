# Talent Hunter Agent

A modern AI-powered talent hunting application built with FastAPI and Streamlit.

## Architecture

This application consists of three main components:

-   **Backend**: FastAPI application providing REST API endpoints (port 8000)
-   **Frontend**: Streamlit web interface for user interaction (port 8501)
-   **Vector Database**: Qdrant vector database for storing and searching embeddings (ports 6333/6334)

## Tech Stack

-   **Backend**: FastAPI, LangChain, LangGraph
-   **Frontend**: Streamlit
-   **Vector Database**: Qdrant
-   **Package Management**: uv
-   **Containerization**: Docker, Docker Compose
-   **Python**: 3.11+

## Prerequisites

Choose one of the following setups:

### Option 1: Docker (Recommended)

-   [Docker](https://docs.docker.com/get-docker/)
-   [Docker Compose](https://docs.docker.com/compose/install/)

### Option 2: Local Development

-   Python 3.11 or higher
-   [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)

## Quick Start

### Using Docker Compose (Recommended)

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd talent-hunter-agent
    ```

2. **Run the application**

    ```bash
    make run-all
    ```

    Or alternatively:

    ```bash
    docker compose up -d
    ```

3. **Access the application**

    - Frontend (Streamlit): http://localhost:8501
    - Backend API (FastAPI): http://localhost:8000
    - API Documentation: http://localhost:8000/docs
    - Qdrant Dashboard: http://localhost:6333/dashboard
    - Qdrant REST API: http://localhost:6333

4. **Stop the application**
    ```bash
    make stop-all
    ```

### Using Local Development

1. **Clone the repository**

    ```bash
    git clone <repository-url>
    cd talent-hunter-agent
    ```

2. **Install dependencies**

    ```bash
    uv sync
    ```

3. **Run the backend**

    ```bash
    uv run uvicorn backend.main:app --host 0.0.0.0 --port 8000 --reload
    ```

4. **Run the frontend** (in a separate terminal)

    ```bash
    uv run streamlit run frontend/ui.py --server.port=8501 --server.address=0.0.0.0
    ```

5. **Access the application**
    - Frontend: http://localhost:8501
    - Backend API: http://localhost:8000
    - API Documentation: http://localhost:8000/docs
    - **Note**: Qdrant is not available in local development mode. Use Docker for full stack testing.

## Available Make Commands

The project includes a Makefile with convenient commands:

```bash
# Build Docker images
make build-backend      # Build only backend image
make build-frontend     # Build only frontend image
make build-all         # Build both images

# Run with Docker
make run-backend       # Run only backend container
make run-frontend      # Run only frontend container
make run-all          # Run both services with docker-compose

# Stop services
make stop-all         # Stop all running services
```

## Development

### Project Structure

```
talent-hunter-agent/
├── backend/
│   ├── agent/          # Agent-related modules
│   └── main.py         # FastAPI application entry point
├── frontend/
│   └── ui.py          # Streamlit application
├── docker-compose.yaml # Multi-service orchestration
├── Dockerfile.fastapi  # Backend container definition
├── Dockerfile.streamlit # Frontend container definition
├── Makefile           # Development commands
├── pyproject.toml     # Python dependencies and configuration
└── uv.lock           # Dependency lock file
```

### Adding Dependencies

To add new Python dependencies:

```bash
uv add <package-name>
```

The dependency will be automatically added to `pyproject.toml` and `uv.lock` will be updated.

### Running Tests

```bash
# Install with dev dependencies
uv sync --group dev

# Run tests (when available)
uv run pytest
```

## Qdrant Vector Database

### Overview

Qdrant is used as the vector database for storing and searching high-dimensional embeddings. It's essential for the AI-powered talent matching capabilities.

### Docker Setup

The Qdrant service is automatically started with the Docker Compose setup:

```bash
# Start all services including Qdrant
make run-all
# or
docker compose up -d
```

### Accessing Qdrant

-   **REST API**: http://localhost:6333
-   **gRPC API**: Port 6334 (for high-performance connections)
-   **Web Dashboard**: http://localhost:6333/dashboard

### From Your Application

When running in Docker, your backend service can connect to Qdrant using:

```python
# Python example using qdrant-client
from qdrant_client import QdrantClient

# Connect from within Docker network
client = QdrantClient(url="http://qdrant:6333")

# Connect from local development (when Qdrant is running in Docker)
client = QdrantClient(url="http://localhost:6333")
```

### Data Persistence

Vector data is persisted in a Docker volume named `qdrant_storage`. This ensures your data survives container restarts.

```bash
# View Qdrant volume
docker volume ls | grep qdrant

# Remove Qdrant data (if needed for testing)
docker volume rm talent-hunter-agent_qdrant_storage
```

### Common Operations

```bash
# View Qdrant logs
docker compose logs qdrant

# Restart only Qdrant
docker compose restart qdrant

# Connect to Qdrant container
docker compose exec qdrant /bin/bash
```

### Troubleshooting

-   **Connection refused**: Ensure Qdrant container is running (`docker compose ps`)
-   **Data not persisting**: Check if volume is properly mounted (`docker volume ls`)
-   **Performance issues**: Monitor resources via the Qdrant dashboard
-   **API errors**: Check Qdrant logs (`docker compose logs qdrant`)

```bash
# Check Qdrant health
curl http://localhost:6333/health

# Check Qdrant cluster info
curl http://localhost:6333/cluster
```

## Troubleshooting

### Port Conflicts

If you encounter port conflicts:

-   Backend (8000): Check if another service is using port 8000
-   Frontend (8501): Check if another Streamlit app is running
-   Qdrant REST API (6333): Check if another Qdrant instance is running
-   Qdrant gRPC (6334): Check for gRPC service conflicts

### Docker Issues

-   Ensure Docker daemon is running
-   Check Docker logs: `docker compose logs`
-   Check specific service logs: `docker compose logs qdrant`
-   Rebuild images: `make build-all`

### Local Development Issues

-   Ensure Python 3.11+ is installed
-   Verify uv installation: `uv --version`
-   Check virtual environment: `uv run python --version`

## Contributing

We welcome contributions to the Talent Hunter Agent project! Please follow these guidelines to ensure a smooth collaboration process.

### Development Workflow

1. **Fork the repository**

    - Click the "Fork" button on the GitHub repository
    - Clone your fork locally:
        ```bash
        git clone https://github.com/YOUR_USERNAME/talent-hunter-agent.git
        cd talent-hunter-agent
        ```

2. **Create a feature branch**

    - Always create a new branch for your changes:
        ```bash
        git checkout -b feature/your-feature-name
        # or for bug fixes:
        git checkout -b fix/bug-description
        ```
    - Use descriptive branch names (e.g., `feature/add-candidate-search`, `fix/login-validation`)

3. **Make your changes**

    - Follow the existing code style and patterns
    - Add comments for complex logic
    - Update relevant documentation if needed
    - Ensure your code follows Python best practices (PEP 8)

4. **Test locally using either Docker or local development setup**

    - **Docker testing** (recommended):
        ```bash
        make build-all
        make run-all
        # Test your changes at http://localhost:8501 and http://localhost:8000
        make stop-all
        ```
    - **Local testing**:
        ```bash
        uv sync
        # Terminal 1: Backend
        uv run uvicorn backend.main:app --reload
        # Terminal 2: Frontend
        uv run streamlit run frontend/ui.py
        ```
    - Test both API endpoints and UI functionality
    - Verify that existing features still work (regression testing)

5. **Submit a pull request**

    **Before submitting:**

    - Commit your changes with clear, descriptive messages:

        ```bash
        git add .
        git commit -m "feat: add candidate search functionality

        - Implement search by skills and experience
        - Add filtering options for location and salary
        - Update UI with search interface
        - Add API endpoints for search operations"
        ```

    - Push your branch to your fork:
        ```bash
        git push origin feature/your-feature-name
        ```

    **Creating the Pull Request:**

    - Go to the original repository on GitHub
    - Click "New Pull Request"
    - Select your branch from your fork
    - Write a PR description

    **PR Description Template:**

    ```markdown
    ## Summary

    Brief description of what this PR accomplishes.

    ## Changes Made

    -   List specific changes
    -   Include new features, bug fixes, or improvements
    -   Mention any new dependencies added
    ```

### Commit Message Guidelines

Use conventional commit format:

-   `feat:` for new features
-   `fix:` for bug fixes
-   `docs:` for documentation changes
-   `style:` for formatting changes
-   `refactor:` for code restructuring
-   `test:` for adding tests
-   `chore:` for maintenance tasks

### Review Process

1. **Automated Checks**: Ensure all CI checks pass (when implemented)
2. **Code Review**: At least one maintainer will review your code

Thank you for contributing to Talent Hunter Agent! 🚀
