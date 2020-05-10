# Makefile

targetdocker = docker-compose.yml
dbdocker = /mnt/dataset/db4mysql/boat/docker-compose.yml
servicename = boatracedocker

start: $(targetdocker)
	docker-compose -f $(targetdocker) up -d

bash: $(pathtodocker)
	docker-compose exec $(servicename) bash

stop: $(targetdocker)
	docker-compose -f $(targetdocker) stop

restart: $(targetdocker)
	docker-compose down && docker-compose -f $(targetdocker) up -d

start_db: $(dbdocker)
	docker-compose -f $(dbdocker) up -d
