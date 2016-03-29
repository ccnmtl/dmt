APP=dmt

JS_FILES=media/js/src/ media/js/tests dmt/main/tests/js
REQUIREJS=$(NODE_MODULES)/.bin/r.js
PY_DIRS=$(APP) features
MAX_COMPLEXITY=7

all: jstest jenkins

include *.mk

behave: check
	$(MANAGE) behave

integration: check $(JS_SENTINAL)
	$(MANAGE) test dmt.main.tests.test_js --settings=$(APP).settings_integration

compose-run:
	docker-compose up

compose-migrate:
	docker-compose run web python manage.py migrate --settings=$(APP).settings_compose

media/main-built.js: $(JS_SENTINAL) build.js media/js/src media/js/libs
	$(REQUIREJS) -o build.js

travis: $(JS_SENTINAL) parallel-tests jstest integration
