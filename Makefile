all: python deps db

python: env requirements.txt
	env/bin/pip install -r requirements.txt

env:
	virtualenv env

deps: vendor/js/angular-1.4.8.js vendor/js/angular-animate-1.4.8.js

vendor/js/angular-1.4.8.js: vendor/js
	curl -o vendor/js/angular-1.4.8.js https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular.js

vendor/js/angular-animate-1.4.8.js: vendor/js
	curl -o vendor/js/angular-animate-1.4.8.js https://ajax.googleapis.com/ajax/libs/angularjs/1.4.8/angular-animate.js

vendor/js:
	mkdir -p vendor/js

vendor/css:
	mkdir -p vendor/css

db: database.db

database.db: create_db.sql
	cat create_db.sql | sqlite3 database.db

dev: secret.key
	-env/bin/python -m flashcards --debug=true || (sleep 1 && make dev)

ipython: env/bin/ipython secret.key
	-env/bin/ipython

secret.key:
	env/bin/python -c "import os; import pickle; pickle.dump(os.urandom(32), open('secret.key', 'wb'), pickle.HIGHEST_PROTOCOL)"

env/bin/ipython: python
	env/bin/pip install ipython

.DELETE_ON_ERROR:
