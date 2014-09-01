#!/bin/bash

docker stop auth${EGO_CONTAINER_ID} 
docker rm  auth${EGO_CONTAINER_ID}
