release:
	@python setup.py sdist bdist_wheel upload
.PHONY: release

testrepl:
	@python tests/testrepl.py repl
.PHONY: testrepl
