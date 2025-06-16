release:
	@python setup.py sdist bdist_wheel upload
.PHONY: release

testrepl:
	@python bin/testrepl.py repl
.PHONY: testrepl

venv:
	@python -m venv .venv
	.venv/bin/pip install --upgrade pip
	.venv/bin/pip install tox
.PHONY: venv

tox: venv
	.venv/bin/tox
.PHONY: tox

clean:
	rm -rf .venv .tox
.PHONY: clean
