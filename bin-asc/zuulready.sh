#!/bin/bash
 
while [ 1 ];
do
    sleep 3
    spark_master_bind_num=`docker ps | grep zuul | wc -l`
    if [ $spark_master_bind_num -ge 1 ]; then
        echo "UPDATE_STATE 'READY'"
    else
        echo "UPDATE_STATE 'TENTATIVE'"
    fi
done
