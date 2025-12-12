.PHONY: help install test lint run docker-build docker-up docker-down clean

help:
	@echo "Available commands:"
	@echo "  make install      - Install dependencies"
	@echo "  make test         - Run tests"
	@echo "  make lint         - Run linter"
	@echo "  make run          - Run the application"
	@echo "  make docker-build - Build Docker image"
	@echo "  make docker-up    - Start services with Docker Compose"
	@echo "  make docker-down  - Stop Docker Compose services"
	@echo "  make clean        - Clean up generated files"

install:
	pip install -r requirements-dev.txt

test:
	pytest --cov=src --cov-report=html --cov-report=term

lint:
	flake8 src tests
	black --check src tests

format:
	black src tests

run:
	uvicorn src.main:app --reload --host 0.0.0.0 --port 8001

docker-build:
	docker build -t matchtal-profile-service:latest .

docker-up:
	docker-compose up -d

docker-down:
	docker-compose down

clean:
	find . -type d -name __pycache__ -exec rm -r {} +
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	rm -rf .pytest_cache
	rm -rf .coverage
	rm -rf htmlcov
	rm -rf dist
	rm -rf build
	rm -rf *.egg-info





