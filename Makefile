clean:
	rm -rf build/

test:
	tox

build:
	rm -f dist/* && python3 setup.py sdist

update_tests: 
	@echo rebuilding har2locust test files
	bash -c 'cd har2locust && ls tests/inputs/ | xargs -I % basename % .har | xargs -I % bash -c "har2locust tests/inputs/%.har > tests/outputs/%.py"'

release: build
	twine upload dist/*
