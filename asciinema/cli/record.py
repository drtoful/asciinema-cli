import sys
import subprocess
import getopt

from asciinema.asciicast import Asciicast

class RecordCommand(object):
    def __init__(self, arguments=[]):
        try:
            opts, commands = getopt.getopt(arguments, "c:t:rqh", ['help'])
        except getopt.error as msg:
            self._help(msg)

        self.cmd = None
        self.title = None
        self.reset = False
        self.quiet = False

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                self._help()
            elif opt in ('-c'):
                self.cmd = arg
            elif opt in ('-t'):
                self.title = arg
            elif opt in ('-r'):
                self.reset = True
            elif opt in ('-q'):
                self.quiet = True

    def _help(self, msg=None):
        if msg is not None:
            print(msg)
            print('')

        print('usage: record [<option>]')
        print('-c <cmd>\tspecify command to execute')
        print('-t <str>\ttitle of the asciicast')
        print('-r\t\treset terminal before recording')
        print('-q\t\tdo not print start and stop messages (quiet)')
        print('-h\t\tprint this help')
        sys.exit(1)

    def execute(self):
        if self.reset:
            self._reset_terminal()

        cast = Asciicast(self.title)

        if not self.quiet:
            print('~ Asciicast recording started.')
            if not self.cmd:
                print('~ Hit ctrl+d or type "exit" to finish.')
            print('')

        cast.record(self.cmd)

        if self.reset:
            self._reset_terminal()

        if not self.quiet:
            print('~ Asciicast recording finished.')

        return cast

    def _reset_terminal(self):
        subprocess.call(["reset"])

