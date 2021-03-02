#!/bin/bash

while true
do
    if [[ $(git --git-dir=/home/pi/programming/python/doorbell_getter/DoorBell/.git --work-tree=/home/pi/programming/python/doorbell_getter/DoorBell/ pull | grep 'Already up to date.' | wc -c ) -eq 0 ]]
    then
        systemctl --user restart doorbell.service
        echo 'doorbell updated'
    fi

    sleep 60s
done
