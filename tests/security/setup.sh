#!/bin/sh

set -e

BZR_HOME=/dev/null bzr export qrt_tests lp:qa-regression-testing/tests

if [ -z $TARGET_PREFIX ] ; then
	echo "RUNNING ON TARGET"
else
	echo "RUNNING FROM HOST"
	adb push qrt_tests /tmp/qrt_tests
fi
