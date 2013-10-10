#!/bin/bash

: ${COUNT:=2}

adb push smem-tabs /home/phablet/

for i in `seq 1 $COUNT`; do
    ${TARGET_PREFIX} "mkdir -p /tmp/results/results/$i"
    ${TARGET_PREFIX} "./smem-tabs -c \"name command uss pss rss vss\" -s pss -r &> /tmp/results/results/$i/smem.log"
    sleep 60
    ${TARGET_PREFIX} "cat /proc/meminfo > /tmp/results/results/$i/meminfo"
done
