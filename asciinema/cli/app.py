import os
import sys

from git import Repo
from git.repo.fun import is_git_dir

from asciinema.cli.record import RecordCommand
from asciinema.cli.list import ListCommand
from asciinema.cli.push import PushCommand
from asciinema.cli.auth import AuthCommand

class AsciinemaCli(object):

    def __init__(self):
        self.dir_home = os.path.join(os.path.expanduser("~"), ".asciinema")
        self.dir_files = os.path.join(self.dir_home, "casts")

        # initialize local repository
        if not is_git_dir(self.dir_files):
            self.cast_repo = Repo.init(self.dir_files, mkdir=True)
            assert not self.cast_repo.bare
        self.cast_repo = Repo(self.dir_files)

    @classmethod
    def run(class_):
        app = class_()
        return app.main()

    def main(self):
        class _Help(object):
            def __init__(self, repo, arguments=[]):
                pass

            def execute(self):
                HELP_TEXT = """usage: %s <command> [-h]

Asciicast recorder+uploader.

Commands:
    record      record asciicast
    list        list recorded asciicast in local repository
    push        upload a specific asciicasto
    auth        authenticate and/or claim recorded asciicasts

Optional arguments:
    -h          display help for a command""" % (sys.argv[0])
                print(HELP_TEXT)

        argv = sys.argv[2:]
        command = None
        if len(sys.argv) > 1:
            command = sys.argv[1]

        class_ = {
            'rec': RecordCommand,
            'record': RecordCommand,
            'ls': ListCommand,
            'list': ListCommand,
            'push': PushCommand,
            'auth': AuthCommand,
        }.get(command, _Help)

        cmd = class_(self.cast_repo, argv)
        cmd.execute()

