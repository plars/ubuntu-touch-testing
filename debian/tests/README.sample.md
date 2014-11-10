# Sample test to be run by the CI team with adt-run

The sample test is really simple test that meets the [CI handoff criteria]
(https://wiki.canonical.com/UbuntuEngineering/CI/HandoffCriteria)

## Resources

This test should be run on an Ubuntu Touch device.

## To run the test

1. Flash an Ubuntu Touch device.
2. Enable adb access on the device.
3. Get the test code:

    $ bzr branch lp:ubuntu-test-cases/sample-adt-test

4. Connect the device to the runner machine with an USB cable.
5. Run the tests with adt-run:

    $ adt-run --built-tree=sample-adt-test --output-dir=output --- ssh -s /usr/share/autopkgtest/ssh-setup/adb

## Test results

The test executable exits with 0 if successful, non-zero otherwise.

## Non-functional stats data

The NFSS json data file will be stored at the output/artifacts/ directory,
along with the file that indicates that it should be uploaded only to the
staging server.

## Triggering

To make sure that we are able to send data from the CI lab using adt-run to the
NFSS server, this test should be run every 24 hours, and every time a new
version of NFSS is deployed to staging.

## Monitoring

work in progress.