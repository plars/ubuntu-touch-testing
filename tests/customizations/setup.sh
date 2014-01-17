#!/bin/sh

set -ex

BZR_HOME=/dev/null bzr export customization_tests lp:savilerow/tests

# copy the autopilot scripts over if needed (ie we are testing from HOST)
[ -z $ANDROID_SERIAL ] || adb push ./customization_tests /home/phablet/autopilot/customization_tests

prepare-autopilot-test.sh
