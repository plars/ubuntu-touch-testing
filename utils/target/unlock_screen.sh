#!/bin/sh

basedir=$(dirname $(readlink -f $0))
powerd-cli active &
pids="$!"
powerd-cli display on &
pids="$pids $!"

sudo -i -u phablet bash -ic "PYTHONPATH=$(pwd) ${basedir}/unlock_screen.py"
rc=$?

for pid in $pids ; do
	kill $pid
done

exit $rc
