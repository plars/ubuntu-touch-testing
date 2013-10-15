#!/bin/bash

: ${COUNT:=10}

adb push smem-tabs /tmp
${TARGET_PREFIX} "chmod +x /tmp/smem-tabs"

for i in `seq 1 $COUNT`; do
    ${TARGET_PREFIX} "mkdir -p /tmp/results/results/$i"
    ${TARGET_PREFIX} "/tmp/smem-tabs -c \"name command uss pss rss vss\" -s pss -r &> /tmp/results/results/$i/smem.log"
    sleep 60
    ${TARGET_PREFIX} "cat /proc/meminfo > /tmp/results/results/$i/meminfo"
done
