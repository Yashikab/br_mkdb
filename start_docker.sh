#!/bin/sh

cd ./docker/

docker-compose start boatracedocker

docker-compose exec boatracedocker bash

cd ..
