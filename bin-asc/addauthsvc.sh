#!/bin/sh

. ./env.sh

dns1=172.17.42.1
dns2=172.17.41.1
dns3=172.17.40.1
 
dns_search_list="auth-service-liberty.local.flyacmeair.net webapp-liberty.local.flyacmeair.net auth-service.local.flyacmeair.net webapp.local.flyacmeair.net eureka.local.flyacmeair.net zuul.local.flyacmeair.net"
dns_search="--dns-search `echo $dns_search_list | sed "s/ / --dns-search /g"`"
 
docker_cmd="docker"

max=$($docker_cmd ps -a | grep 'auth[0-9]\+ *$' | sed 's/.*auth\([0-9]\+\).*/\1/' | sort -n | tail -n 1)
num=$(expr $max + 1)

$docker_cmd run \
-d -t -P \
--dns "$dns1" \
--dns "$dns2" \
--dns "$dns3" \
$dns_search \
--name auth$num -h auth$num.auth-service${as_suffix}.local.flyacmeair.net \
acmeair/auth-service${as_suffix}

while [ 1 ];
do
  sleep 14
done



