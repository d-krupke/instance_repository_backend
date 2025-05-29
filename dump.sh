#!/bin/bash
sudo docker compose down
# remove the volumes corresponding to the containers
echo "If you changed some schema, uncomment the next line to prune the database volumes and trigger a rebuild of the schema."
#sudo docker volume rm "$(sudo docker volume ls -q --filter "name=instance_repository_backend")"
# delete all `/instances` directories in ./REPOSITORY/*/instances
sudo find ./REPOSITORY/*/instances -type d -exec rm -rf {} +
