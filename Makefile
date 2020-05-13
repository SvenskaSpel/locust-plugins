clean:
	rm -rf build/

build:
	rm -f dist/* && python3 setup.py sdist

release: build
	twine upload dist/*
