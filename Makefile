MANAGE=./manage.py
APP=dmt
FLAKE8=./ve/bin/flake8

jenkins: ./ve/bin/python check jshint jscs flake8 test

travis: ./ve/bin/python check jshint jscs flake8 test integration

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint media/js/src/ media/js/tests

jscs: node_modules/jscs/bin/jscs
	./node_modules/jscs/bin/jscs media/js/src/ media/js/tests

js: node_modules/.bin/r.js
	./node_modules/.bin/r.js -o build.js

behave: ./ve/bin/python check
	$(MANAGE) test bdd_tests --behave_browser firefox --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner

behave-wip: ./ve/bin/python check
	$(MANAGE) test bdd_tests --behave_no-capture --behave_tags @wip --behave_browser firefox --testrunner=django_behave.runner.DjangoBehaveTestSuiteRunner

node_modules/jshint/bin/jshint:
	npm install jshint --prefix .

node_modules/jscs/bin/jscs:
	npm install jscs@1.8.1 --prefix .

node_modules/.bin/r.js:
	npm install requirejs --prefix .

test: ./ve/bin/python
	npm install
	$(MANAGE) jenkins --pep8-exclude=migrations --enable-coverage --coverage-rcfile=.coveragerc
	npm test

integration: ./ve/bin/python
	npm install
	$(MANAGE) jenkins --settings=dmt.settings_integration
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
