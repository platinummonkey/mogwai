.PHONY: clean-pyc ext-test test upload-docs docs coverage

all: clean-pyc test

test:
	bash run_tests.sh

coverage:
	bash run_coverage.sh

release:
	python scripts/make-release.py

tox-test:
	PYTHONDONTWRITEBYTECODE= tox

clean:
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '#*' -exec rm -f {} +
	find . -name '.#*' -exec rm -f {} +
	find . -name '.bak' -exec rm -f {} +

docs:
	sphinx-build docs html
