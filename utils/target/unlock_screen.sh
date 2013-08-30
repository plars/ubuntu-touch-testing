#!/bin/sh

basedir=$(dirname $(readlink -f $0))

#temporary workaround for bug #1207386
chmod 666 /dev/uinput
sudo -i -u phablet bash -ic "PYTHONPATH=$(pwd) ${basedir}/unlock_screen.py"
