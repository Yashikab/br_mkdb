# Makefile

targetdocker = docker-compose.yml
dbdocker = ./local_mysql/docker-compose.yml
servicename = boatracedocker

start: $(targetdocker)
	docker-compose -f $(targetdocker) up -d

bash: $(pathtodocker)
	docker-compose exec $(servicename) bash

down: $(targetdocker)
	docker-compose -f $(targetdocker) down

restart: $(targetdocker)
	docker-compose down && docker-compose -f $(targetdocker) up -d

start_db: $(dbdocker)
	docker-compose -f $(dbdocker) up -d

down_db: $(dbdocker)
	docker-compose -f $(dbdocker) down
