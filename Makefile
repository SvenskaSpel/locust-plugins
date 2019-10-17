clean:
	rm -rf build/

build:
	rm -f dist/* && python3 setup.py sdist bdist_wheel

release: build
	twine upload dist/*
