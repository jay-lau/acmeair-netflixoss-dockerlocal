#!/bin/bash

docker stop webapp${EGO_CONTAINER_ID} 
docker rm  webapp${EGO_CONTAINER_ID}
