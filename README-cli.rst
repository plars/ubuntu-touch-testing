Touch Testing From the CLI
==========================

The touch testing execution framework was written so that its very easy to
run tests from home in the exact same way test are run in the lab. The only
things you need are:

 * This bzr branch
 * The phablet-tools_ and ubuntu-device-flash_ packages
 * An Ubuntu Touch supported_ device

.. _phablet-tools: http://launchpad.net/phablet-tools
.. _ubuntu-device-flash: http://launchpad.net/goget-ubuntu-touch
.. _supported: http://wiki.ubuntu.com/Touch/Devices

There are two pieces to touch testing, provisioning and test execution. These
functions are independent of one another. i.e., if your device already
has the proper image/configuration, you can simply use the test-runner.

Provisioning
------------

The provisioning script is a simple wrapper to commands from phablet-tools
to get a device ready for testing. Provisioning is performed with the
scripts/provision.sh command. Running::

  ./scripts/provision.sh -h

will list supported options.

Provisioning using this script requires that you start off with the
device booted and accessible via ADB. The device will be rebooted
automatically and completely reinstalled - ALL DATA WILL BE LOST.

NOTE: provision.sh requires a path to a network-manager wifi connection that
can be copied to the target device. By default this is set to
${HOME}/.ubuntu-ci/wifi.conf. This can be overridden with the -n parameter.

By default, the latest devel-proposed image will be installed. If you
wish to install the latest ubuntu-rtm image instead, use::

  export IMAGE_OPT="--bootstrap --developer-mode --channel=ubuntu-touch/ubuntu-rtm/14.09-proposed"
  ./scripts/provision.sh -w

Executing Tests
---------------

The touch testing repository supports both autopilot and UTAH test definitions.

Executing Autopilot Tests
~~~~~~~~~~~~~~~~~~~~~~~~~

One or more autopilot tests can be run on the target device using the command::

  ./scripts/run-autopilot-tests.sh

This is a small wrapper that uses phablet-tools to drive the tests. The
script can run one or more autopilot tests. By default it will reboot the
device between each test and ensure the device is settled using the
*system-settle* script. Both of those options can be disabled via command
line options. By default the script will create a directory named
*clientlogs* and then a subdirectory for each testsuite with result files.
These sub-directories include a xUnit XML formatted file, *test_results.xml*,
as well as several log files from the device to help with debugging failures.

NOTE: run-autopilot-tests.sh will call a script that installs 
unity8-autopilot if it is not already installed, to allow the device to
be unlocked automatically.

An example testing two applications::

 ./scripts/run-autopilot-tests.sh -a dropping_letters_app -a music_app

Executing UTAH Tests
~~~~~~~~~~~~~~~~~~~~

Executing UTAH tests locally will require you to install the UTAH client
package from a PPA::

  sudo add-apt-repository ppa:utah/stable
  sudo apt-get update
  sudo apt-get install utah-client

With that package installed UTAH tests can be run with::

  ./scripts/jenkins.sh

This script runs one test at a time and will put its test artifacts under the
*clientlogs* directory similar to the autopilot runner. The UTAH result file
will be named clientlogs/utah.yaml.

An example of running the sdk test suite::

  ./scripts/jenkins.sh -a sdk

Provisioning and Executing tests for an MP
------------------------------------------

These scripts are used by jenkins for the testing of MPs that generate Debian
packages. To re-create the testing performed by jenkins, set the following
environment variables based on the jenkins build parameters::

  export package_archive=<from jenkins build parameter>
  export test_packages=<from jenkins build parameter>
  export test_suite=<from jenkins build parameter>

and set the variable::

  export ANDROID_SERIAL=<adb id from your test device>

Then execute the following script::

  ./scripts/run-mp.sh

Running Tests for a Modified Click Application
----------------------------------------------

First provision the device with the desired image using the instructions
in the "Provisioning" section of this README.

Once the image has been provisioned, install the click app to test.
The dropping-letters application is used in this example::

  adb push com.ubuntu.dropping-letters_0.1.2.2.67_all.click /tmp
  adb shell pkcon --allow-untrusted install-local \
      /tmp/com.ubuntu.dropping-letters_0.1.2.2.67_all.click

Now install the test sources ('--wipe' will remove any previously installed
test sources)::

  phablet-click-test-setup --wipe --click com.ubuntu.dropping-letters

The above phablet-click-test-setup command will install the standard test
dependencies and the click application's test sources as specified in the
manifest. This is usually the application's trunk branch. To override the test
sources with local changes, replace the test sources that were copied to the
device. This example assumes the application code is checked out under the
'dropping-letters' directory with the test sources under 'tests/autopilot'::

  adb shell rm -rf /home/phablet/autopilot/dropping_letters_app
  adb push dropping-letters/tests/autopilot \
      /home/phablet/autopilot

Finally, run the application tests::

  ./scripts/run-autopilot-tests.sh -a dropping_letters_app

The test results are available under::

  clientlogs/dropping_letters_app/test_results.xml

Running Tests for a Modified Debian Package
-------------------------------------------

First provision the device with the desired image using the instructions
in the "Provisioning" section of this README.

If the device is provisioned, and you have built the debian package
you wish to test with locally, install it on the device. For instance,
if you are building and installing dialer-app::

  phablet-config writable-image -r 0000 --package-dir /path/to/packages -p dialer-app

Alternatively, if you have built the packages in a ppa, you could use::

  phablet-config writable-image -r 0000 --ppa ppa:ci-train-ppa-service/landing-004 -p dialer-app

NOTE: If you have updates to the dependencies or tests in debian
packages, make sure to also install packages for those if required for
the change you are making. Some tests need a few extra dependencies 
installed for the tests to function correctly.  To see a list of them, 
look at jenkins/testconfig.py.

Finally, run the application tests::

  ./scripts/run-autopilot-tests.sh -a dropping_letters_app

The test results are available under::

  clientlogs/dropping_letters_app/test_results.xml

