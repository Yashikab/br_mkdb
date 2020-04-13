# Makefile

pathtodocker = ./docker
targetdocker = $(pathtodocker)/docker-compose.yml
servicename = boatracedocker

start: $(targetdocker)
	docker-compose -f $(targetdocker) start

bash: $(pathtodocker)
	cd $(pathtodocker); docker-compose exec $(servicename) bash

stop: $(targetdocker)
	docker-compose -f $(targetdocker) stop
