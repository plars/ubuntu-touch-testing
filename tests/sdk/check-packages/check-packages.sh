#!/bin/sh

set -e

BZR_HOME=/dev/null bzr export tests lp:ubuntu-qtcreator-plugins/tests/device

if [ -z $TARGET_PREFIX ] ; then
	echo "RUNNING ON TARGET"
	./tests/check-packages
else
	echo "RUNNING FROM HOST"
	adb push ./tests/check-packages /tmp/
	adb-shell "chmod +x /tmp/check-packages; /tmp/check-packages"
fi
