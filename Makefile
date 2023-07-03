.PHONY: docs clean

COMMAND = docker-compose run --rm app /bin/bash -c

all: build test

build:
	docker-compose build

up:
	docker-compose up -d

down:
	docker-compose down

restart:
	docker-compose restart

shell:
	docker-compose run --rm app jiraworkflow/manage.py shell

createsuperuser:
	docker-compose run --rm app jiraworkflow/manage.py createsuperuser

makemigrations:
	docker-compose run --rm app jiraworkflow/manage.py makemigrations

migrate:
	docker-compose run --rm app jiraworkflow/manage.py migrate

collectstatic:
	docker-compose run --rm app jiraworkflow/manage.py collectstatic --no-input

check: checksafety checkstyle

test:
	$(COMMAND) "pip install tox && tox -e test"

checksafety:
	$(COMMAND) "pip install tox && tox -e checksafety"

checkstyle:
	$(COMMAND) "pip install tox && tox -e checkstyle"

coverage:
	$(COMMAND) "pip install tox && tox -e coverage"

clean:
	rm -rf build
	rm -rf jiraworkflow.egg-info
	rm -rf dist
	rm -rf htmlcov
	rm -rf .tox
	rm -rf .cache
	rm -rf .pytest_cache
	find . -type f -name "*.pyc" -delete
	rm -rf $(find . -type d -name __pycache__)
	rm .coverage
	rm .coverage.*

dockerclean:
	docker system prune -f
	docker system prune -f --volumes

imageremove:
	docker rmi $(docker images -a -q)