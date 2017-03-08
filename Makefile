APP=dmt

JS_FILES=media/js/src/ media/js/tests
REQUIREJS=$(NODE_MODULES)/.bin/r.js
PY_DIRS=$(APP) features
MAX_COMPLEXITY=7

all: jstest eslint js jenkins

include *.mk

behave: check
	$(MANAGE) behave

integration: check $(JS_SENTINAL)
	$(MANAGE) test --settings=$(APP).settings_integration

compose-run:
	docker-compose up

compose-migrate:
	docker-compose run web python manage.py migrate --settings=$(APP).settings_compose

media/main-built.js: $(JS_SENTINAL) build.js media/js/src media/js/libs
	$(REQUIREJS) -o build.js

media/chat-built.js: $(JS_SENTINAL) chat-build.js media/js/src/chat.js media/js/libs
	$(REQUIREJS) -o chat-build.js

travis: $(JS_SENTINAL) parallel-tests jstest integration

js: media/main-built.js media/chat-built.js

eslint: $(JS_SENTINAL) media/js/src
	$(NODE_MODULES)/.bin/eslint media/js/src/**

.PHONY: js
