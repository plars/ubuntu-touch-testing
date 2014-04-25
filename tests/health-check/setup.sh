#!/bin/sh -x
echo "Setting up"

${TARGET_PREFIX} apt-get install health-check

${TARGET_PREFIX} mkdir -p /tmp/results

adb push . /tmp/healthcheck

exit 0
