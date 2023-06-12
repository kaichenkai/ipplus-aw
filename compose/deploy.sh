#!/bin/bash

set -x

#ALL_SERVERS=("es1" "es2" "es3")
#ALL_SERVERS=("ds1")
ALL_SERVERS=("es0")


deploy() {

    for i in ${ALL_SERVERS[@]}
    do
        ssh ${i} "sudo mkdir -p /data/darkeye/compose; sudo chown app:app /data/darkeye/compose"
        ssh ${i} "sudo chown app:app /data/"
        ssh ${i} "sudo mkdir -p /data/es/data; sudo mkdir -p /data/es/logs; sudo chmod 777 -R /data/es/data/; sudo chmod 777 -R /data/es/logs/"
        scp -r ${i} ${i}:/data/darkeye/compose
        ssh ${i} "cd /data/darkeye/compose/${i}; docker-compose up --build -d"
    done
}


deploy
