MANAGE=./manage.py
APP=dmt
FLAKE8=./ve/bin/flake8

jenkins: ./ve/bin/python validate test flake8

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

test: ./ve/bin/python
	npm install
	$(MANAGE) jenkins
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
	rm -rf ve
	rm -rf media/CACHE
	rm -rf reports
	rm -f celerybeat-schedule
	rm -f .coverage
	find . -name '*.pyc' -exec rm {} \;
	npm rm casperjs karma karma-junit-reporter karma-phantomjs-launcher \
		karma-qunit karma-requirejs phantomjs qunitjs requirejs

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
