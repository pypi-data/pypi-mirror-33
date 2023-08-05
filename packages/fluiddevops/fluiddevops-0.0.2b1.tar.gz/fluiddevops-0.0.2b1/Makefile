
help:
	@echo "targets: develop and install"

develop:
	python setup.py develop

install:
	python setup.py install

clean:
	rm -rf build dist

deploy: clean
	python setup.py sdist
	python setup.py bdist_wheel
	twine upload dist/*
