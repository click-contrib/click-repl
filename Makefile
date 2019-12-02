.PHONY: init test release testrepl

init:
	@pip3.6 install -r requirements.txt
	@pip3.6 install -e .

test:
	@pytest tests

release:
	@python setup.py sdist bdist_wheel upload

testrepl:
	@python bin/testrepl.py repl

