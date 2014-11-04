Touch Testing From the CLI
==========================

The touch testing execution framework was written so that its very easy to
run tests from home in the exact same way test are run in the lab. The only
thigs you need are:

 * This bzr branch
 * The phablet-tools_ package
 * An Ubuntu Touch supported_ device

.. _phablet-tools: http://launchpad.net/phablet-tools
.. _supported: http://wiki.ubuntu.com/Touch/Devices

There are two pieces to touch testing, provisioning and test execution. These
functions are independent of one another. eg, If your device already
has the proper image/configuration, you can simply use the test-runner.

Provisioning
------------

The provisioning script is a simple wrapper to commands from phablet-tools
to get a device ready for testing. Provisioning is performed with the
scripts/provision.sh command. Running::

  ./scripts/provision.sh -h

will list supported options.

NOTE: provision.sh requires a path to a network-manager wifi connection that
can be copied to the target device. By default this is set to
${HOME}/.ubuntu-ci/wifi.conf. This can be overriden with the -n parameter.

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

Provisioning and Executiong tests for an MP
-------------------------------------------

These scripts are used by jenkins for the testing of MPs that generate debian
packages. To re-create the testing performed by jenkins, set the following
environment variables based on the jenkins build parameters::

  export package_archive=<from jenkins build parameter>
  export test_packages=<from jenkins build parameter>
  export test_suite=<from jenkins build parameter>

and set the variable::

  export ANDROID_SERIAL=<adb id from your test device>

Then execute the following script::

  wget ${package_archive}
  unzip archive
  package_dir=archive
  package_list=""
  for package in ${test_packages}; do
      package_list="-p ${package} ${package_list}"
  done
  export SKIP_CLICK=1
  export SKIP_TESTCONFIG=1
  ./scripts/provision.sh -s ${ANDROID_SERIAL} -n ${HOME}/.ubuntu-ci/wifi.conf \
          -D ${package_dir} ${package_list}
  ./scripts/run-smoke -s ${ANDROID_SERIAL} -n -a ${test_suite}

