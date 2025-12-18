.PHONY: help install test lint demo demo-gif demo-svg clean

help:
	@echo "MCP Readiness Scanner - Development Commands"
	@echo ""
	@echo "Available targets:"
	@echo "  make install      Install the package in development mode"
	@echo "  make test         Run tests with pytest"
	@echo "  make lint         Run linting with ruff"
	@echo "  make demo-gif     Generate demo GIF (requires asciinema + agg)"
	@echo "  make demo-svg     Generate demo SVG (requires termtosvg)"
	@echo "  make demo         Alias for demo-gif"
	@echo "  make clean        Remove build artifacts and caches"

install:
	pip install -e ".[dev]"

test:
	pytest

lint:
	ruff check mcpreadiness tests

demo-gif:
	@echo "Generating demo GIF..."
	./scripts/generate_demo.sh

demo-svg:
	@echo "Generating demo SVG..."
	./scripts/generate_demo_svg.sh

demo: demo-gif

clean:
	rm -rf build/
	rm -rf dist/
	rm -rf *.egg-info
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf demos/temp
	find . -type d -name __pycache__ -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
