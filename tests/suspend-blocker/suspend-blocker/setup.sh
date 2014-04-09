#!/bin/bash

${TARGET_PREFIX} mkdir -p /tmp/results
${TARGET_PREFIX} mkdir -p /tmp/suspend-blocker
adb push suspend-blocker /tmp/suspend-blocker
adb push susblock.conf /home/phablet/.config/upstart
${TARGET_PREFIX} chmod +x /tmp/suspend-blocker/suspend-blocker
${TARGET_PREFIX} chown phablet.phablet /home/phablet/.config/upstart/susblock.conf
${TARGET_PREFIX} rm -f /home/phablet/.cache/upstart/susblock.log

