#!/bin/sh

set -e

adb-shell PKGS=\"$PKGS\" /home/phablet/bin/prepare-autopilot-test.sh

[ -n "$NO_UNLOCK" ] || reboot-and-unlock.sh
