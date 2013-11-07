#!/bin/sh

set -e

# autolists create subdirectories for each test and we are launched from
# there. go a up a directory to get where we need to be:
cd ..

# tslist.auto just lists the basenames of files as the test cases, so
# we have to figure out the full path here so we can run it
script=$(find ./qrt_tests -name $1)

if [ -z $TARGET_PREFIX ] ; then
	echo "RUNNING ON TARGET"
	$script
else
	echo "RUNNING FROM HOST"
	# the setup.sh script copied the repo under /tmp
	adb-shell "/tmp/$script"
fi
