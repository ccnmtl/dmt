MANAGE=./manage.py
APP=dmt
FLAKE8=./ve/bin/flake8

./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

test: ./ve/bin/python
	$(MANAGE) jenkins

flake8: ./ve/bin/python
	$(FLAKE8) $(APP) --max-complexity=10

runserver: ./ve/bin/python
	$(MANAGE) runserver

migrate: ./ve/bin/python
	$(MANAGE) migrate

validate: ./ve/bin/python
	$(MANAGE) validate

shell: ./ve/bin/python
	$(MANAGE) shell_plus

jenkins: ./ve/bin/python
	make validate
	make test
	make flake8

clean:
	rm -rf ve
	rm -rf media/CACHE
	rm -rf reports
	rm celerybeat-schedule
	rm .coverage
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
