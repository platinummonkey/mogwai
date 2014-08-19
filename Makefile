.PHONY: clean test tox-test docs coverage

all: clean test coverage release tox-test docs

test:
	bash run_tests.sh

coverage:
	bash run_coverage.sh

release:
	python setup.py sdist upload

tox-test:
	PYTHONDONTWRITEBYTECODE= tox

clean:
    rm -Rf mogwai.egg-info || true
    rm -Rf coverage || true
    rm -Rf .tox || true
    rm -Rf html || true
    rm -Rf build || true
    rm -Rf dist || true
	find . -name '*.pyc' -exec rm -f {} +
	find . -name '*.pyo' -exec rm -f {} +
	find . -name '*~' -exec rm -f {} +
	find . -name '#*' -exec rm -f {} +
	find . -name '.#*' -exec rm -f {} +
	find . -name '.bak' -exec rm -f {} +

docs:
	sphinx-build docs html
