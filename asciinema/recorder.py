import os
import shlex

import asciinema.timer as timer
from asciinema.pty_recorder import PtyRecorder


class Recorder(object):
    def __init__(self):
        self.pty_recorder = PtyRecorder()

    def record(self, cmd=None):
        """
        start recording given command.

        :param cmd: can be a string or a triple (function, args, kwargs)
                    or :py:class:`None`. If a triple is given, the function
                    will be called with the given arguments, otherwise
                    the string will be executed as a command.
        """
        def _record_cmd(command):
            command = shlex.split(command)
            os.execlp(command[0], *command)

        if not cmd:
            cmd = os.environ.get('SHELL', '/bin/sh')

        if isinstance(cmd, str):
            cmd = (_record_cmd, (cmd,), {})

        return timer.timeit(self.pty_recorder.record_command, cmd)
