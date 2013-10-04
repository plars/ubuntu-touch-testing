#!/bin/sh

basedir=$(dirname $(readlink -f $0))

nohup powerd-cli active&
sudo -i -u phablet bash -ic "PYTHONPATH=$(pwd) ${basedir}/unlock_screen.py"
