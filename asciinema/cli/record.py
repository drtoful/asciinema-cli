import os
import sys
import subprocess
import getopt

from asciinema.asciicast import Asciicast

class RecordCommand(object):
    def __init__(self, repo, arguments=[]):
        try:
            opts, commands = getopt.getopt(arguments, "c:t:rqh", ['help'])
        except getopt.error as msg:
            self._help(msg)

        self.cmd = None
        self.title = None
        self.reset = False
        self.quiet = False
        self.repo = repo

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

        HELP_TEXT = """record [-c <cmd>] [-t <str>] [-r] [-q] [-h]

records a new Asciicast and stores it in local repository.

Optional arguments:
    -c <cmd>        specify command to execute
    -t <str>        title of the new asciicast
    -r              reset terminal before recording
    -q              do not print messages (quiet)
    -h              print this help"""
        print(HELP_TEXT)
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

        # save in local git repository
        filename = os.path.join(self.repo.working_dir, cast.id+".asciicast")

        with open(filename, "w") as fp:
            cast.save(fp)

        self.repo.index.add([filename])
        self.repo.index.commit("update recording '"+cast.id+"'")

        if not self.quiet:
            print('~ Asciicast recording finished.')

    def _reset_terminal(self):
        subprocess.call(["reset"])

