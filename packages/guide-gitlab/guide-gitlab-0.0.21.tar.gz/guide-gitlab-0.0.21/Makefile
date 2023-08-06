# This file contains common administration commands. It is language-independent.

.PHONY: clean clean-build clean-pyc

# Run this with 'make integration' or 'make report="true" integration'
integrationtest: clean-pyc
	python3 -m pytest -v -s integration_tests

integrationtestcoverage:
	py.test --cov-report term --cov=guide_gitlab integration_tests


clean-build:
	-@rm -fr build/
	-@rm -fr *.egg-info
	-@rm -fr dist/

clean-pyc:
	-@find . -name '*.pyc' -exec rm -f {} +
	-@find . -name '*.pyo' -exec rm -f {} +
	-@find . -name '*~' -exec rm -f {} +
	-@find . -name '__pycache__' -exec rm -fr {} +

clean: clean-build clean-pyc


dist: clean-build
	@python setup.py sdist bdist_wheel

zipdist: clean-build
	@python setup.py sdist --format zip

publish:
	@twine upload dist/*