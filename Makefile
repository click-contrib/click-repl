release:
	@python setup.py sdist bdist_wheel upload
.PHONY: release

testrepl:
	@python bin/testrepl.py repl
.PHONY: testrepl
