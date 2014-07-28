import os
import subprocess
import time
import struct
import functools
import random
import hashlib
import types
import json

from asciinema.recorder import Recorder


class Asciicast(object):
    """
    Basic class representing a Asciicast.

    :param title: title of Asciicast
    :param id: unique id of Asciicast

    .. py:attribute:: recording

        data of the last recording as a list of triples
        in the form (seconds, microseconds, data)

    .. py:attribute:: meta_data

        meta data information of this asciicast. this is
        a dictionary with the following keys:
        id, username, duration, title, command, shell, term
    """

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
        self.lines = 80
        self.columns = 25
        self.id = id if id is not None else self._generate_id()

    def record(self, cmd=None, recorder=None, *args, **kwargs):
        """
        Start recording the TTY output of a given command.

        :param cmd: the command to record the output. can be a string or a
                    python function 'pointer'. :py:class:`None` will start
                    the default system shell.
        :param recorder: the :py:class:`~.recorder.Recorder` object to use
                         for the recordings
        :param kwargs: when using a python function as command, you can
                         provide any number of arguments to this method, that
                         get passed to the function.

        This shows a simple example how to record the output of a python
        method.

        .. code-block:: python

            from asciinema.asciicast import Asciicast

            def print_fancy(message):
                print "~~~ %s ~~~" % message

            cast = Asciicast()
            cast.record(print_fancy, message="Hello World!")

        Every call to this method will update `recording` and `meta_data`
        accordingly.
        """
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

        # create list containing triples
        #  (seconds, microseconds, payload)
        # -> this corresponds more or less an entry in a ttyrec
        #    file
        for line in stdout.timing.split("\n"):
            timing, bytes = line.split(" ", 1)
            secs, microsecs = timing.split(".", 1)

            secs, microsecs, bytes = int(secs), int(microsecs), int(bytes)
            self.recording += [(secs, microsecs, data[i:i+bytes])]
            i += bytes

        # store the number of lines and columns after the execution
        self.lines = int(get_command_output(['tput', 'lines']))
        self.columns = int(get_command_output(['tput', 'cols']))

        # store meta data information for the command
        #  -> store string if a string is provided
        #  -> store which function was called and with which options,
        #     if the command is a python function
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

    def save(self, file):
        """
        saves the content of this asciicast object to a specified file.
        the contents of the file will be a JSON dictionary. it contains
        the meta data and the recording.

        :param file: a :py:class:`file` like object (open file descriptor
                     handler)
        """
        data = {'meta': self.meta_data, 'data': self.recording}
        json.dump(data, file)

    @classmethod
    def load(class_, file):
        """
        loads a previously saved Asciicast.

        :param file: a :py:class:`file` like object (open file descriptor
                     handler)

        :returns: a new Asciicast object
        """
        data = json.load(file)

        self = class_()
        self.recording = data['data']
        self.username = data['meta']['username']
        self.duration = data['meta']['duration']
        self.title = data['meta']['title']
        self.command = data['meta']['command']
        self.shell = data['meta']['shell']
        self.term = data['meta']['term']['type']
        self.lines = data['meta']['term']['lines']
        self.columns = data['meta']['term']['columns']
        self.id = data['meta']['id']

        return self

    def upload(self, uploader):
        """
        uploading the asciicast to a remote repository

        :param uploader: the :py:class:`~.uploader.Uploader` to be
                         used for uploading

        :returns: URL were the uploaded Asciicast can be accessed at
        """
        return uploader.upload(self)

    def as_ttyrec(self):
        """
        convert Asciicast to a ttyrec compatible file

        :returns: ttyrec compatible string
        """
        def _converter(secs, microsecs, data):
            return struct.pack("<I", secs) + struct.pack("<I", microsecs) + \
                struct.pack("<I", len(data)) + data

        return "".join([_converter(*x) for x in self.recording])

    @property
    def meta_data(self):
        return {
            'id': self.id,
            'username': self.username,
            'duration': self.duration,
            'title': self.title,
            'command': self.command,
            'shell': self.shell,
            'term': {
                'type': self.term,
                'lines': self.lines,
                'columns': self.columns
            }
        }


def get_command_output(args):
    process = subprocess.Popen(args, stdout=subprocess.PIPE)
    return process.communicate()[0].strip()
