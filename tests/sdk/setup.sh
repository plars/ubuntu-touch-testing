#!/bin/sh

set -e

BZR_HOME=/dev/null bzr export qt_tests lp:ubuntu-qtcreator-plugins/tests/device

if [ -z $TARGET_PREFIX ] ; then
	echo "RUNNING ON TARGET"
else
	echo "RUNNING FROM HOST"
	adb push qt_tests /tmp/qt_tests
fi
