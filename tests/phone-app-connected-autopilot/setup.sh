#!/bin/sh

set -ex

# we have issues with running the test too soon, this is a hack:
echo "SLEEPING 60 TO HELP MAKE SURE PHONE IS READY"
sleep 60


if [ -z $ANDROID_SERIAL ] ; then
	# set up the config file for the test
	NUMBER=$(./sms_self.py --list)
	cat ./testnumbers.cfg | sed -e "s/TODO/+$NUMBER/" > /home/phablet/.testnumbers.cfg

	# remove old logs so the receive test will work
	rm /home/phablet/.local/share/TpLogger/logs/ofono_ofono_account0/* -rf

	# now send an sms to ourself
	./sms_self.py
else
	echo "test running from host"
	adb push ./sms_self.py /home/phablet/autopilot/

	# set up the config file for the test
	NUMBER=$(adb-shell /home/phablet/autopilot/sms_self.py --list | head -n1)
	cat ./testnumbers.cfg | sed -e "s/TODO/+$NUMBER/" > .testnumbers.cfg
	adb push .testnumbers.cfg /home/phablet/.testnumbers.cfg
	rm .testnumbers.cfg

	# remove old logs so the receive test will work
	adb-shell rm /home/phablet/.local/share/TpLogger/logs/ofono_ofono_account0/* -rf
	adb-shell /home/phablet/autopilot/sms_self.py
fi

sleep 10s  # try and let the message come through
PKGS="phone-app-connected-autopilot" prepare-autopilot-test.sh
