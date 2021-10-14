# shellcheck disable=SC1113
#/bin/bash

docker-compose stop
docker-compose rm -f

docker-compose build
docker-compose up -d