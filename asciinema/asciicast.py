import os
import subprocess
import time
import struct
import functools
import random
import hashlib
import types

from asciinema.recorder import Recorder

class Asciicast(object):

    def _generate_id(self):
        md5 = hashlib.md5()
        md5.update(str(random.random()))
        return md5.hexdigest()[:8]

    def __init__(self, title=None, id=None):
        self.title = title
        self.shell = os.environ.get('SHELL', '/bin/sh')
        self.term = os.environ.get('TERM')
        self.username = os.environ.get('USER')
        self.recording = []
        self.id = id if id is not None else self._generate_id()

    def record(self, cmd=None, recorder=None, *args, **kwargs):
        if recorder is None:
            recorder = Recorder()

        if isinstance(cmd, str) or cmd is None:
            self.command = cmd
        else:
            self.command = (cmd, args, kwargs)

        self.duration, stdout = recorder.record(cmd=self.command)
        self.recording = []

        data = stdout.data
        i = 0

        for line in stdout.timing.split("\n"):
            timing, bytes = line.split(" ", 1)
            secs, microsecs = timing.split(".", 1)

            secs, microsecs, bytes = int(secs), int(microsecs), int(bytes)
            self.recording += [ (secs, microsecs, data[i:i+bytes]) ]
            i += bytes

    def upload(self, uploader=None):
        pass

    def as_ttyrec(self):
        def _converter(secs, microsecs, data):
            return struct.pack("<I", secs)+struct.pack("<I", microsecs)+ \
                struct.pack("<I", len(data))+data

        return "".join([_converter(*x) for x in self.recording])

    @property
    def meta_data(self):
        lines = int(get_command_output(['tput', 'lines']))
        columns = int(get_command_output(['tput', 'cols']))

        command = self.command
        if not isinstance(command, str) and command is not None:
            method, args, kwargs = command
            module = method.__module__
            if isinstance(method, types.MethodType):
                module = module+"."+method.im_class.__name__
            command = {
                'pyfunc': module+"."+method.__name__,
                'args': args,
                'kwargs': kwargs
            }

        return {
            'username'   : self.username,
            'duration'   : self.duration,
            'title'      : self.title,
            'command'    : command,
            'shell'      : self.shell,
            'term'       : {
                'type'   : self.term,
                'lines'  : lines,
                'columns': columns
            }
        }


def get_command_output(args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    return process.communicate()[0].strip()
