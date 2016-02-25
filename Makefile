APP=dmt

JS_FILES=media/js/src/ media/js/tests dmt/main/tests/js
REQUIREJS=$(NODE_MODULES)/.bin/r.js
PY_DIRS=$(APP) bdd_tests
MAX_COMPLEXITY=7

all: jstest jenkins

include *.mk

behave: check
	$(MANAGE) test bdd_tests --behave_browser firefox --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner

behave-wip: check
	$(MANAGE) test bdd_tests --behave_no-capture --behave_tags @wip --behave_browser firefox --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner

integration: check $(JS_SENTINAL)
	$(MANAGE) jenkins --settings=$(APP).settings_integration

compose-run:
	docker-compose up

compose-migrate:
	docker-compose run web python manage.py migrate --settings=$(APP).settings_compose

media/main-built.js: $(JS_SENTINAL) build.js media/js/src media/js/libs
	$(REQUIREJS) -o build.js

travis: $(JS_SENTINAL) jenkins jstest integration
