# Makefile

targetdocker = docker-compose.yml
dbdocker = ../mysql_local/boat/
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
	cd $(dbdocker) && docker-compose up -d

down_db: $(dbdocker)
	cd $(dbdocker) && docker-compose down

start_gdb:
	cd ./proxy && pipenv run bash start_gsql.sh

down_gdb:
	cd ./proxy && pipenv run bash down_gsql.sh
