#!/bin/bash
sudo docker compose down
# remove the volumes corresponding to the containers
sudo docker volume rm "$(sudo docker volume ls -q --filter "name=instance_repository_backend")"
# delete all `/instances` directories in ./REPOSITORY/*/instances
sudo find ./REPOSITORY/*/instances -type d -exec rm -rf {} +
