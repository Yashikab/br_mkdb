# Makefile

targetdocker = docker-compose.yml
servicename = boatracedocker

start: $(targetdocker)
	docker-compose -f $(targetdocker) up -d

bash: $(pathtodocker)
	docker-compose exec $(servicename) bash

stop: $(targetdocker)
	docker-compose -f $(targetdocker) stop

restart: $(targetdocker)
	docker-compose down && docker-compose -f $(targetdocker) up -d
