MANAGE=./manage.py
APP=dmt
FLAKE8=./ve/bin/flake8

REQUIREMENTS=requirements.txt
NODE_MODULES=./node_modules
JS_SENTINAL=$(NODE_MODULES)/sentinal
JSHINT=$(NODE_MODULES)/jshint/bin/jshint
JSCS=$(NODE_MODULES)/jscs/bin/jscs
REQUIREJS=$(NODE_MODULES)/.bin/r.js

jenkins: ./ve/bin/python check jshint jscs flake8 test

travis: ./ve/bin/python check jshint jscs flake8 test integration

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

jshint: $(JS_SENTINAL)
	$(JSHINT) media/js/src/ media/js/tests

jscs: $(JS_SENTINAL)
	$(JSCS) media/js/src/ media/js/tests

$(JS_SENTINAL): package.json
	rm -rf $(NODE_MODULES)
	npm install
	touch $(JS_SENTINAL)

media/main-built.js: $(JS_SENTINAL) build.js media/js/src
	$(REQUIREJS) -o build.js

behave: ./ve/bin/python check
	$(MANAGE) test bdd_tests --behave_browser firefox --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner

behave-wip: ./ve/bin/python check
	$(MANAGE) test bdd_tests --behave_no-capture --behave_tags @wip --behave_browser firefox --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner

test: ./ve/bin/python $(JS_SENTINAL)
	$(MANAGE) jenkins --pep8-exclude=migrations --enable-coverage --coverage-rcfile=.coveragerc
	npm test

integration: ./ve/bin/python $(JS_SENTINAL)
	$(MANAGE) jenkins --settings=$(APP).settings_integration
	npm test

flake8: ./ve/bin/python
	$(FLAKE8) $(APP) bdd_tests --exclude=migrations --max-complexity=7

runserver: ./ve/bin/python check
	$(MANAGE) runserver

migrate: ./ve/bin/python check jenkins
	$(MANAGE) migrate

check: ./ve/bin/python
	$(MANAGE) check

shell: ./ve/bin/python
	$(MANAGE) shell_plus

compose-run:
	docker-compose up

compose-migrate:
	docker-compose run web python manage.py migrate --settings=$(APP).settings_compose

clean:
	rm -rf ve media/CACHE reports node_modules
	rm -f celerybeat-schedule .coverage
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make check
	make test
	make migrate
	make flake8

rebase:
	git pull --rebase
	make check
	make test
	make migrate
	make flake8

# run this one the very first time you check
# this out on a new machine to set up dev
# database, etc. You probably *DON'T* want
# to run it after that, though.
install: ./ve/bin/python check jenkins
	createdb $(APP)
	$(MANAGE) migrate

include *.mk
