.PHONY: run test lint typecheck rom verify clean

# Launch HOM GUI
run:
	PYTHONPATH=src python -m hijaiyyah

# Run all tests
test:
	pytest tests/ -v --tb=short

# Run tests with coverage
test-cov:
	pytest tests/ -v --cov=src/hijaiyyah --cov-report=html

# Lint with ruff
lint:
	ruff check src/ tests/

# Type check with mypy
typecheck:
	mypy src/hijaiyyah/

# Generate ROM image
rom:
	python tools/rom_generator.py

# Verify Master Table integrity
verify:
	python tools/table_verifier.py

# Clean build artifacts
clean:
	find . -type d -name __pycache__ -exec rm -rf {} +
	rm -rf .pytest_cache htmlcov .mypy_cache dist build *.egg-info
