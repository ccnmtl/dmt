./ve/bin/python: requirements.txt bootstrap.py virtualenv.py
	./bootstrap.py

jenkins: ./ve/bin/python
	./manage.py jenkins

flake8: ./ve/bin/python
	./ve/bin/flake8 dmt --max-complexity=10

runserver: ./ve/bin/python
	./manage.py runserver

migrate: ./ve/bin/python
	./manage.py migrate

clean:
	rm -rf ve
	find . -name '*.pyc' -exec rm {} \;

pull:
	git pull
	make jenkins
	make migrate
	make flake8

rebase:
	git pull --rebase
	make jenkins
	make migrate
	make flake8
