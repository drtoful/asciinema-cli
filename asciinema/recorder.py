import os
import shlex

import asciinema.timer as timer
from asciinema.pty_recorder import PtyRecorder


class Recorder(object):

    def __init__(self):
        self.pty_recorder = PtyRecorder()

    def record(self, cmd=None):
        def _record_cmd(command):
            command = shlex.split(command)
            os.execlp(command[0], *command)

        if not cmd:
            cmd = os.environ.get('SHELL', '/bin/sh')

        if isinstance(cmd, str):
            cmd = (_record_cmd,(cmd,),{})

        return timer.timeit(self.pty_recorder.record_command, cmd)

