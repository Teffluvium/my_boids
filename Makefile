.DEFAULT_GOAL := help

.PHONY: help
help: 	## Show this help message
	@uv run python -c "import re; \
	[[print(f'\033[36m{m[0]:<20}\033[0m {m[1]}') for m in re.findall(r'^([a-zA-Z_-]+):.*?## (.*)$$', open(makefile).read(), re.M)] for makefile in ('$(MAKEFILE_LIST)').strip().split()]"

.PHONY: install
install: ## Install dependencies using uv
	uv sync

.PHONY: format
format: ## Format code using ruff
	uv run ruff format .

.PHONY: lint
lint: 	## Check code for linting issues
	uv run ruff check .

.PHONY: lint-fix
lint-fix: ## Auto-fix linting issues where possible
	uv run ruff check --fix .

.PHONY: type-check
type-check: ## Run mypy type checking
	uv run mypy src/my_boids tests

.PHONY: test
test: ## Run tests with coverage
	uv run pytest tests/ --cov=my_boids --cov-report=html --cov-report=term

.PHONY: run
run: ## Run the boids simulation
	uv run my-boids

.PHONY: clean
clean: ## Remove generated files and caches
	find . -type d -name "__pycache__" -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type f -name "*.pyo" -delete
	find . -type f -name "*.pyd" -delete
	rm -rf .pytest_cache
	rm -rf .ruff_cache
	rm -rf .mypy_cache
	rm -rf htmlcov
	rm -rf mypy_report
	rm -rf .coverage

all: format lint type-check test
	@echo "All checks passed!"
