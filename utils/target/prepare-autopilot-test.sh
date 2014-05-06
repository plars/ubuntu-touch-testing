#!/bin/sh

set -e

#installs dependencies so an autopilot test case can run

if [ -n "$PKGS" ] ; then
	MISSING=0
	dpkg -s $PKGS 2>/dev/null >/dev/null || MISSING=1
	if [ $MISSING -eq 1 ] ; then
		apt-get install -yq --force-yes $PKGS
	else
		echo "setup not needed"
	fi
fi
exit 0
