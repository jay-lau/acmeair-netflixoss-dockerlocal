#!/bin/sh


dns_addr=172.17.42.1

/root/gyliu/acmeair-netflixoss-dockerlocal/bin-asc/egodocker.py run --debug --logfile /tmp/dns.log  -p ${dns_addr}:53:53/udp -p ${dns_addr}:8080:8080/tcp --name skydns crosbymichael/skydns -nameserver 8.8.8.8:53 -domain "flyacmeair.net"
