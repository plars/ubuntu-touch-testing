#!/bin/bash
set -ex

cleanup() {
	#In case anything goes wrong, try to leave the device attached
	ncd_usb.py -u http://qa-relay-control -b 0 -r 0 on
}

trap cleanup TERM INT EXIT

${TARGET_PREFIX} rm -f /var/log/kern.log
${TARGET_PREFIX} restart rsyslog
${TARGET_PREFIX} sudo -iu phablet start susblock

#Turn off the USB port for this device
ncd_usb.py -u http://qa-relay-control -b 0 -r 0 off 
sleep 1800
#Turn on the USB port for this device
ncd_usb.py -u http://qa-relay-control -b 0 -r 0 on
${TARGET_PREFIX} sudo -iu phablet stop susblock
${TARGET_PREFIX} /tmp/suspend-blocker/suspend-blocker -rbH -o /tmp/results/kern.json /var/log/kern.log
${TARGET_PREFIX} cp /var/log/kern.log /tmp/results
