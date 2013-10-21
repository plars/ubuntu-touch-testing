#!/bin/sh

basedir=$(dirname $(readlink -f $0))
powerd-cli active &
powerd-cli display on &

sudo -i -u phablet bash -ic "PYTHONPATH=$(pwd) ${basedir}/unlock_screen.py"
