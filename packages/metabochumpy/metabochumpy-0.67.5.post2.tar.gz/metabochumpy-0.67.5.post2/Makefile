all:

upload:
	python setup.py register sdist upload

test:
	python -m unittest discover -s chumpy

coverage: clean qcov
qcov: all
	env LD_PRELOAD=$(PRELOADED) coverage run --source=. -m unittest discover -s .
	coverage html
	coverage report -m
