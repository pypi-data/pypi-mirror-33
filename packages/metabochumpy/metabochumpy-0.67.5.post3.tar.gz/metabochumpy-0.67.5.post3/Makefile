all:

upload:
	rm -r dist
	python setup.py sdist
	twine upload dist/*

test:
	python -m unittest

coverage: clean qcov
qcov: all
	env LD_PRELOAD=$(PRELOADED) coverage run --source=. -m unittest discover -s .
	coverage html
	coverage report -m
