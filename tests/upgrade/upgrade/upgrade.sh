#!/bin/sh

## upgrades the given target
## Intersting environment variables that must be set:
##  ANDROID_SERIAL - specify another android device
ANDROID_SERIAL="${ANDROID_SERIAL-015d1884b20c1c0f}"  #doanac's nexus7 at home

set -eux

export ANDROID_SERIAL=$ANDROID_SERIAL

phablet_reboot_wait() {
	# TODO get this into phablet-tools
	adb reboot
	adb shell stop android-tools-adbd 2>/dev/null || true
	adb wait-for-device
	# sometimes wait-for-device comes back too quick, so wait once more
	sleep 4s
	adb wait-for-device
}

# try and get the system up with an actual wlan0
phablet_get_interface() {
	if ! adb shell ifconfig -a | grep wlan0 >/dev/null ; then
		return 1
	fi
}

# try and try and try to get an IP
# network is flaky, this seems to help:
phablet_get_ip() {
	adb shell nmcli c list
	uuid=$(adb shell nmcli c list | grep 802-11-wireless | tail -n1 | grep -o -E "[a-f0-9]{8}-([a-f0-9]{4}-){3}[a-f0-9]{12}")
	tmp=$(mktemp)
	adb shell sh -c "nmcli c up uuid $uuid ; echo ANDROID_RC=$?" | tee $tmp
	rc=1
	if grep "ANDROID_RC=0" $tmp >/dev/null; then
		rc=0
	fi
	rm $tmp
	return $rc
}

retry() {
	cmd=$1
	retries=$2

	for i in $(seq $retries) ; do
		if $cmd ; then
			return 0
		fi
		times=$(($retries - $i))
		if [ $times -ne 0 ] ; then
			echo "$cmd: failed, retrying $(($retries - $i)) more times"
			[ -z $reboot ] || phablet_reboot_wait
			sleep 60
		else
			echo "$cmd: failed after $retries attempts"
		fi
	done
	return 1
}

orig_version=$(adb shell system-image-cli -b)
echo $orig_version | sed -e 's/build number/UPGRADING FROM VERSION/'

reboot=1 retry phablet_get_interface 4
sleep 60
retry phablet_get_ip 4

adb shell system-image-cli -v
adb wait-for-device
new_version=$(adb shell system-image-cli -b)
echo $new_version | sed -e 's/build number/UPGRADED TO VERSION/'

if [ "$new_version" = "$orig_version" ] ; then
	echo "UPGRADE FAILED"
	exit 1
fi
