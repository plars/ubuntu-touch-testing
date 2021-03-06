#!/bin/sh
set -e

basedir=$(dirname $(readlink -f $0))

if ! adb-shell dpkg -s unity8-autopilot 2>/dev/null >/dev/null ; then
	echo "Installing unity8-autopilot as a pre-req for unlocking screen"
        # Installation some times fails due to not being able to
        # resolve derived.archive.canonical.com. 
        # So retry a couple of more times
	adb shell "sudo apt-get install -yq --force-yes unity8-autopilot || \
sudo apt-get install -yq --force-yes unity8-autopilot || \
sudo apt-get install -yq --force-yes unity8-autopilot"
fi

adb pull /usr/share/unity8/unlock-device "${basedir}"
chmod +x "${basedir}/unlock-device"

# unlock-device will reboot for us
exec "${basedir}/unlock-device" -w $basedir/../../scripts/reboot-and-wait
