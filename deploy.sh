#!/bin/bash

set -x

cp .env /data/envfile/ipplus.env
cp .mysql /data/envfile/mysql.env
docker-compose up -d --build
