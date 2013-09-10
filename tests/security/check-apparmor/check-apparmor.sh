#!/bin/sh

set -e

if [ -z $TARGET_PREFIX ] ; then
	echo "RUNNING ON TARGET"
	../image/privileged/check-apparmor
else
	echo "RUNNING FROM HOST"
	adb push ../image/privileged/check-apparmor /tmp/
	adb-shell "chmod +x /tmp/check-apparmor; /tmp/check-apparmor"
fi
