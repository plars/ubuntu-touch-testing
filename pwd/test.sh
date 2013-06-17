#!/bin/bash
echo pwd is: $(pwd)
echo Changing to /tmp...
cd /tmp
echo Checking that cd worked...
echo directory is now $(pwd), should be /tmp
/usr/bin/test `pwd` == '/tmp'
