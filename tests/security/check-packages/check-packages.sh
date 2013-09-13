#!/bin/sh

set -e

if [ -z $TARGET_PREFIX ] ; then
	echo "RUNNING ON TARGET"
	../image/unprivileged/check-packages
else
	echo "RUNNING FROM HOST"
	adb push ../image/unprivileged/check-packages /tmp/
	adb-shell "chmod +x /tmp/check-packages; /tmp/check-packages"
fi
