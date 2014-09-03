#!/bin/sh
 
dns_addr=172.17.42.1
 
./egodocker.py run --debug --logfile /tmp/dock.log --name skydock -v /var/run/docker.sock:/docker.sock crosbymichael/skydock -ttl 30 -environment local -s /docker.sock -domain "flyacmeair.net" -name skydns

