#!/bin/sh -x
echo "Setting up"

${TARGET_PREFIX} sudo apt-get install -y health-check python3-psutil

${TARGET_PREFIX} mkdir -p /tmp/results

adb push . /tmp/healthcheck

exit 0
