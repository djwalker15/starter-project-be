.PHONY: install run test cov fmt lint type qa docker-up docker-down

install:
	pip install -U pip
	pip install -r requirements-dev.txt

run:
	uvicorn app.main:app --reload --host 127.0.0.1 --port $${PORT:-8000}

test:
	pytest

cov:
	coverage run -m pytest && coverage html && coverage report -m

fmt:
	black .
	ruff check --fix .

lint:
	ruff check .

type:
	mypy app

qa: fmt lint type test
