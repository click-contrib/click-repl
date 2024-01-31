release:
	@python3 setup.py sdist bdist_wheel upload
.PHONY: release

build-dev:
	@python3 setup.py sdist bdist_wheel
.PHONY: build-dev

testrepl:
	@python3 bin/testrepl.py repl
.PHONY: testrepl
