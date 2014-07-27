import os
import subprocess
import time


class Asciicast(object):

    def __init__(self, title=None):
        self.title = title
        self.shell = os.environ.get('SHELL', '/bin/sh')
        self.term = os.environ.get('TERM')
        self.username = os.environ.get('USER')

    def record(self, recorder=None):
        pass

    def upload(self, uploader=None):
        pass

    @property
    def meta_data(self):
        lines = int(get_command_output(['tput', 'lines']))
        columns = int(get_command_output(['tput', 'cols']))

        return {
            'username'   : self.username,
            'duration'   : self.duration,
            'title'      : self.title,
            'command'    : self.command,
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
