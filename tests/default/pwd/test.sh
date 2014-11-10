#!/bin/sh

set -e

if [ -n "$TARGET_PREFIX" ] ; then
	echo "RUNNING FROM HOST"
else
	echo "RUNNING ON TARGET"
	TARGET_PREFIX="/bin/sh -c"
fi

#when it comes from adb we get a \r\n that should be removed
dir=$($TARGET_PREFIX "cd /tmp; pwd" | head -n1 | tr -d '\r\n')
if [ $dir != "/tmp" ] ; then
	echo "failed to change directory"
	exit 1
fi
exit 0
