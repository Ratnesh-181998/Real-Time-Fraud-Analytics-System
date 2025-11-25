# Makefile for Real-Time Fraud Analytics System

.PHONY: help install run-api run-ui test clean lint format docker-build docker-run

# Default target
help:
	@echo "Real-Time Fraud Analytics System - Available Commands:"
	@echo ""
	@echo "  make install        - Install all dependencies"
	@echo "  make run-api        - Start the FastAPI server"
	@echo "  make run-ui         - Start the web dashboard"
	@echo "  make run-all        - Start both API and UI"
	@echo "  make test           - Run all tests"
	@echo "  make lint           - Run code linting"
	@echo "  make format         - Format code with black"
	@echo "  make clean          - Clean temporary files"
	@echo "  make docker-build   - Build Docker image"
	@echo "  make docker-run     - Run in Docker container"
	@echo ""

# Install dependencies
install:
	@echo "Installing Python dependencies..."
	pip install -r requirements.txt
	@echo "Installing Web UI dependencies..."
	cd web-ui && npm install
	@echo "Installation complete!"

# Run API server
run-api:
	@echo "Starting FastAPI server..."
	cd src && python api_server.py

# Run Web UI
run-ui:
	@echo "Starting Web Dashboard..."
	cd web-ui && python -m http.server 3000

# Run both API and UI
run-all:
	@echo "Starting both API and UI..."
	@echo "API will run on http://localhost:8000"
	@echo "UI will run on http://localhost:3000"
	start cmd /k "cd src && python api_server.py"
	start cmd /k "cd web-ui && python -m http.server 3000"

# Run tests
test:
	@echo "Running tests..."
	pytest tests/ -v --cov=src

# Lint code
lint:
	@echo "Running linters..."
	flake8 src/ --max-line-length=100
	mypy src/ --ignore-missing-imports

# Format code
format:
	@echo "Formatting code..."
	black src/ tests/
	@echo "Code formatted!"

# Clean temporary files
clean:
	@echo "Cleaning temporary files..."
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.log" -delete
	rm -rf .pytest_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info
	@echo "Cleanup complete!"

# Docker build
docker-build:
	@echo "Building Docker image..."
	docker build -t fraud-analytics:latest .

# Docker run
docker-run:
	@echo "Running Docker container..."
	docker run -p 8000:8000 -p 3000:3000 fraud-analytics:latest

# Create necessary directories
setup-dirs:
	mkdir -p logs
	mkdir -p models/saved
	mkdir -p data

# Train models
train-models:
	@echo "Training fraud detection models..."
	python src/models/xgboost_model.py
	python src/models/autoencoder_model.py
	@echo "Models trained and saved!"

# Generate synthetic data
generate-data:
	@echo "Generating synthetic transaction data..."
	python data/synthetic_data_generator.py

# Run simulation
simulate:
	@echo "Running transaction simulation..."
	python src/simulate_transactions.py

# View logs
logs:
	tail -f logs/api_server.log

# Check system status
status:
	@echo "Checking system status..."
	curl http://localhost:8000/health || echo "API is not running"
	curl http://localhost:3000 || echo "UI is not running"
