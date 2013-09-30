#!/bin/bash

${TARGET_PREFIX} mkdir -p /tmp/results
NO_UNLOCK=1 PKGS="eventstat" prepare-autopilot-test.sh
#Let the system quiet down for a little while
sleep 300

