import os
import json
import sys

from git import Repo
from git.repo.fun import is_git_dir
from asciinema.asciicast import Asciicast

from asciinema.cli.record import RecordCommand
from asciinema.cli.list import ListCommand

class AsciinemaCli(object):

    def __init__(self):
        self.dir_home = os.path.join(os.path.expanduser("~"), ".asciinema")
        self.dir_files = os.path.join(self.dir_home, "casts")

        # initialize local repository
        if not is_git_dir(self.dir_files):
            self.cast_repo = Repo.init(self.dir_files, mkdir=True)
            assert not self.cast_repo.bare
        self.cast_repo = Repo(self.dir_files)

    def do_record(self, arguments=[]):
        # do recording
        cmd = RecordCommand(arguments)
        cast = cmd.execute()

        # save in local git repository
        filename = os.path.join(self.dir_files, cast.id+".asciicast")

        with open(filename, "w") as fp:
            cast.save(fp)

        self.cast_repo.index.add([filename])
        self.cast_repo.index.commit("update recording '"+cast.id+"'")

    def do_list(self, arguments=[]):
        ls = ListCommand(self.cast_repo)
        ls.doit()

    def do_help(self):
        print >>sys.stderr, "usage: %s <command>" % sys.argv[0]

    @classmethod
    def run(class_):
        app = class_()
        return app.main()

    def main(self):
        argv = sys.argv[2:]
        command = sys.argv[1]

        if command == "rec" or command == "record":
            self.do_record(argv)
        elif command == "ls" or command == "list":
            self.do_list(argv)
        else:
            self.do_help()



