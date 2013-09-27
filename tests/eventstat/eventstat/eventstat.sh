#!/bin/bash
: ${DURATION:=60}
: ${COUNT:=10}
${TARGET_PREFIX} "echo \"{\\\"duration\\\": $DURATION, \\\"count\\\": $COUNT}\" > /tmp/results/options.json"
${TARGET_PREFIX} "eventstat -CSl -r /tmp/results/eventstat.csv $DURATION $COUNT > /tmp/results/eventstat.log"
