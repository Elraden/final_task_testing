
PYTHON ?= python
PIP ?= $(PYTHON) -m pip
export PYTHONIOENCODING := utf-8

.PHONY: install test mutate mutate_fast htmlcov results clean

install:
	$(PIP) install -r requirements.txt

test:
	$(PYTHON) -m pytest -q

mutate:
	$(PYTHON) -m mutmut run

mutate_fast:
	$(PYTHON) -m mutmut run --since $(shell git merge-base main HEAD)

htmlcov:
	$(PYTHON) -m pytest --cov=billing --cov-report=html

results:
	$(PYTHON) -m mutmut results

clean:
	rm -rf .mutmut_cache htmlcov .coverage
