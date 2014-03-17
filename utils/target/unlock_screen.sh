#!/bin/sh

basedir=$(dirname $(readlink -f $0))

if ! dpkg -s unity8-autopilot 2>/dev/null >/dev/null ; then
	echo "Installing unity8-autopilot as a pre-req for unlocking screen"
	apt-get install -yq --force-yes unity8-autopilot
fi

sudo -i -u phablet bash -ic "PYTHONPATH=$(pwd) ${basedir}/unlock_screen.py"
rc=$?

exit $rc
