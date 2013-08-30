#!/bin/sh

set -e

# copy the autopilot scripts over if needed
[ -z $ANDROID_SERIAL ] || adb push ./ubuntu_test_cases /home/phablet/autopilot/ubuntu_test_cases

PKGS="camera-app-autopilot gallery-app-autopilot mediaplayer-app-autopilot webbrowser-app-autopilot" prepare-autopilot-test.sh
