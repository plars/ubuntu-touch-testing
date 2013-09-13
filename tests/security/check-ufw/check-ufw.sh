#!/bin/sh

set -e

if [ -z $TARGET_PREFIX ] ; then
	echo "RUNNING ON TARGET"
	../image/privileged/check-ufw
else
	echo "RUNNING FROM HOST"
	adb push ../image/privileged/check-ufw /tmp/
	adb-shell "chmod +x /tmp/check-ufw; /tmp/check-ufw"
fi
