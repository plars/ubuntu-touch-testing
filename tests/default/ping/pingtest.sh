#!/bin/sh

set -e

if [ -z $TARGET_PREFIX ] ; then
    echo "RUNNING ON TARGET"
    ping -c 5 $(ip route show | head -n1 |cut -d" " -f3)
else
    echo "RUNNING FROM HOST"
    ${TARGET_PREFIX} ping -c 5 '$(ip route show | head -n1 |cut -d" " -f3)'
fi

