#!/usr/bin/env python

import subprocess
import threading


class TimeoutError(Exception):
    pass


class TimeoutCommand(object):
    def __init__(self, cmd):
        self.cmd = cmd
        self.proc = None

    def run(self, timeout):
        def target():
            self.proc = subprocess.Popen(self.cmd, stdout=subprocess.PIPE,
                                         stderr=subprocess.PIPE)
            self.stdout, self.stderr = self.proc.communicate()

        thread = threading.Thread(target=target)
        thread.start()
        thread.join(timeout)
        if thread.is_alive():
            self.proc.terminate()
            thread.join()
            raise TimeoutError(
                "stdout: {0}\nstderr: {1}".format(self.stdout, self.stderr))
        return (self.proc.returncode, self.stdout, self.stderr)
