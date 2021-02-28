# Makefile

targetdocker = docker-compose.yml
targetdocker_local = docker-compose_wo_gpu.yml
dbdocker = ./local_mysql/docker-compose.yml
servicename = boatracedocker

start: $(targetdocker)
	poetry run docker-compose -f $(targetdocker) up -d

bash: $(pathtodocker)
	poetry run docker-compose exec $(servicename) bash

down: $(targetdocker)
	poetry run docker-compose -f $(targetdocker) down

restart: $(targetdocker)
	poetry run docker-compose down && poetry run docker-compose -f $(targetdocker) up -d

start_local: $(targetdocker_local)
	poetry run docker-compose -f $(targetdocker_local) up -d

down_local: $(targetdocker_local)
	poetry run docker-compose -f $(targetdocker_local) down

restart_local: $(targetdocker_local)
	poetry run docker-compose down && poetry run docker-compose -f $(targetdocker_local) up -d


start_db: $(dbdocker)
	poetry run docker-compose -f $(dbdocker) up -d

down_db: $(dbdocker)
	poetry run docker-compose -f $(dbdocker) down
