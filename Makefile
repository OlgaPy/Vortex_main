.PHONY: makemigrations migrate build shell

makemigrations:
	docker-compose exec kapibara-monolith ./manage.py makemigrations

migrate:
	docker-compose exec kapibara-monolith ./manage.py migrate

build:
	docker-compose build --no-cache

shell:
	docker-compose exec kapibara-monolith ./manage.py shell_plus
