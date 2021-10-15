clean:
	rm -rf build/

test:
	tox

build:
	rm -f dist/* && python3 setup.py sdist

release: build
	twine upload dist/*
