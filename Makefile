.PHONY: test lint format-check typecheck validate evaluate build-submission experiment

test:
	python -m pytest

lint:
	python -m ruff check .

format-check:
	python -m ruff format --check .

typecheck:
	python -m mypy src

validate:
	python -m riscv_parameter_extractor validate

evaluate:
	python -m riscv_parameter_extractor evaluate

experiment:
	python -m riscv_parameter_extractor experiment

build-submission:
	python -m riscv_parameter_extractor build-submission
