#!/bin/sh

set -e

adb-shell PKGS=\"$PKGS\" prepare-autopilot-test.sh
