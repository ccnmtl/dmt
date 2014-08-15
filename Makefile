MANAGE=./manage.py
APP=dmt
FLAKE8=./ve/bin/flake8

jenkins: ./ve/bin/python validate jshint jscs flake8 test

travis: ./ve/bin/python validate jshint jscs flake8 integration

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

jshint: node_modules/jshint/bin/jshint
	./node_modules/jshint/bin/jshint media/js/src/ media/js/tests

jscs: node_modules/jscs/bin/jscs
	./node_modules/jscs/bin/jscs media/js/src/ media/js/tests


node_modules/jshint/bin/jshint:
	npm install jshint --prefix .

node_modules/jscs/bin/jscs:
	npm install jscs --prefix .

test: ./ve/bin/python
	npm install
	npm install ./vendor/karma-junit-reporter.tar.gz
	$(MANAGE) jenkins
	npm test

integration: ./ve/bin/python
	npm install
	npm install ./vendor/karma-junit-reporter.tar.gz
	$(MANAGE) jenkins --settings=dmt.settings_integration
	npm test

flake8: ./ve/bin/python
	$(FLAKE8) $(APP) --max-complexity=7

runserver: ./ve/bin/python validate
	$(MANAGE) runserver

migrate: ./ve/bin/python validate jenkins
	$(MANAGE) migrate

validate: ./ve/bin/python
	$(MANAGE) validate

shell: ./ve/bin/python
	$(MANAGE) shell_plus

clean:
	rm -rf ve media/CACHE reports node_modules
	rm -f celerybeat-schedule .coverage
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make validate
	make test
	make migrate
	make flake8

rebase:
	git pull --rebase
	make validate
	make test
	make migrate
	make flake8

# run this one the very first time you check
# this out on a new machine to set up dev
# database, etc. You probably *DON'T* want
# to run it after that, though.
install: ./ve/bin/python validate jenkins
	createdb $(APP)
	$(MANAGE) syncdb --noinput
	make migrate
