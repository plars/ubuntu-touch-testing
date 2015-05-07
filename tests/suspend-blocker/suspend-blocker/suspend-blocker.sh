#!/bin/bash
set -ex

cleanup() {
	#In case anything goes wrong, try to leave the device attached
	ncd_usb.py -u http://bos01-a-04-shelf04-relay -b 0 -r 0 on
}

trap cleanup TERM INT EXIT

${TARGET_PREFIX} sudo rm -f /var/log/syslog
${TARGET_PREFIX} sudo restart rsyslog
${TARGET_PREFIX} start susblock

#Turn off the USB port for this device
ncd_usb.py -u http://bos01-a-04-shelf04-relay -b 0 -r 0 off 
sleep 100
#Turn on the USB port for this device
ncd_usb.py -u http://bos01-a-04-shelf04-relay -b 0 -r 0 on
# Wait for the device to come back
timeout 300 adb wait-for-device
# If we can't stop susblock, it's probably because it already stopped itself
${TARGET_PREFIX} stop susblock || /bin/true
${TARGET_PREFIX} sudo /tmp/suspend-blocker/suspend-blocker -rbH -o /tmp/results/kern.json /var/log/syslog
${TARGET_PREFIX} sudo cp /var/log/syslog /tmp/results
${TARGET_PREFIX} sudo chown -R phablet.phablet /tmp/results
