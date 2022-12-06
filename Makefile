PYTHON = python3
PIP = pip3
POETRY ?= poetry

ifeq ($(OS), Darwin)
	OPEN := open
else
	OPEN := xdg-open
endif

.PHONY: init
init:
	$(POETRY) install

.PHONY: yapf
yapf:
	$(POETRY) run yapf -r --diff .

.PHONY: flake8
flake8:
	$(POETRY) run flake8 . \
		--select=E9,F63,F7,F82 \
		--show-source \
		--statistics
	# Full linter run.
	$(POETRY) run flake8 --max-line-length=96 .

.PHONY: format
format:
	make flake8; make yapf

.PHONY: test
test:
	$(POETRY) run pytest

.PHONY: coverage
coverage:
	$(POETRY) run pytest --cov-report html:coverage \
		--cov=src/bundle_basic \
		--cov=src/bundle_debug \
		--cov=src/bundle_media \
		tests/
	$(OPEN) coverage/index.html

.PHONY: run
run:
	$(PYTHON) runner.py

.PHONY: create_app
create_app:
	$(PYTHON) create_app.py

.PHONY: publish_queue
publish_queue:
	$(PYTHON) publish_queue.py