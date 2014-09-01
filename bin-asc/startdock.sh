#!/bin/sh
 
dns_addr=172.17.42.1
 
docker run -d --name skydock -v /var/run/docker.sock:/docker.sock crosbymichael/skydock -ttl 30 -environment local -s /docker.sock -domain "flyacmeair.net" -name skydns

while [ 1 ];
do
  sleep 14
done
~     
