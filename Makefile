.PHONY: makemigrations migrate build shell bash test run-for-loadtest run

migrations:
	docker-compose exec kapibara-monolith ./manage.py makemigrations

migrate:
	docker-compose exec kapibara-monolith ./manage.py migrate

build:
	docker-compose build --no-cache

shell:
	docker-compose exec kapibara-monolith ./manage.py shell_plus

bash:
	docker-compose exec kapibara-monolith bash

test:
	docker-compose exec kapibara-monolith pytest

run-for-loadtest:
	docker-compose -f docker-compose.yml -f docker-compose.loadtest.yml up

run:
	docker-compose up
