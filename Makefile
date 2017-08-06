
PYTHON_ENV ?= development
GUNICORN_NUM_WORKERS ?= 15
GUNICORN_BIND_HOST ?= localhost
GUNICORN_BIND_PORT ?= 3005

.PHONY: clean
clean:
	rm -Rf test/*.pyc
	find api -name '*.pyc' -delete

.PHONY: env
env:
	virtualenv env
	./env/bin/pip install -r requirements.txt

UNIT_TEST_FILES := $(wildcard test/*_test.py test/routes/*_test.py)
.PHONY: test
test: $(UNIT_TEST_FILES)
	PYTHON_ENV=test $(foreach file,$(UNIT_TEST_FILES),./env/bin/python $(file);)

INTEGRATION_TEST_FILES := $(wildcard test/integration/*_test.py)
.PHONY: test.integration
test.integration: $(INTEGRATION_TEST_FILES)
	PYTHON_ENV=test $(foreach file,$(INTEGRATION_TEST_FILES),./env/bin/python $(file);)

.PHONY: gunicorn
gunicorn:
	export PYTHON_ENV=$(PYTHON_ENV) && ./env/bin/python ./bin/ensure_fixtures && ./env/bin/gunicorn --access-logfile - --error-logfile - --workers=$(GUNICORN_NUM_WORKERS) --bind=$(GUNICORN_BIND_HOST):$(GUNICORN_BIND_PORT) run:app
