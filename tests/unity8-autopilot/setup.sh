#!/bin/sh

set -e

NO_UNLOCK=1 PKGS="unity8-autopilot" prepare-autopilot-test.sh
$TARGET_PREFIX sudo -i -u phablet stop unity8
