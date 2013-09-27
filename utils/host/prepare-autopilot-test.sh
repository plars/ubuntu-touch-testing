#!/bin/sh

set -e

adb-shell NO_UNLOCK=\"$NO_UNLOCK\" PKGS=\"$PKGS\" /home/phablet/bin/prepare-autopilot-test.sh
