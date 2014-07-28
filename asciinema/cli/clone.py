import getopt
import functools
import sys
import os

from git import Blob
from asciinema.asciicast import Asciicast


class CloneCommand(object):
    def __init__(self, repo, arguments=[]):
        try:
            opts, commands = getopt.getopt(arguments, "h", ['help'])
        except getopt.error as msg:
            self._help(msg)

        self.repo = repo

        if len(commands) == 0:
            self._help("no asciicast id specified")
        self.id = commands[0]

        for opt, arg in opts:
            if opt in ('-h', '--help'):
                self._help()

    def _help(self, msg=None):
        sys.exit(1)

    def execute(self):
        def _predicate_file(file, item, depth):
            if depth > 1:
                return False

            if not isinstance(item, Blob):
                return False

            return item.path == file

        try:
            head = self.repo.active_branch.commit
            files = [x for x in head.tree.traverse(
                predicate=functools.partial(
                    _predicate_file, str(self.id)+".asciicast"
                )
            )]
            if len(files) == 0:
                raise Exception()

            # load old cast and rename id (thus cloning it)
            old_id = self.id
            cast = Asciicast.load(files[0].data_stream)
            cast.id = cast._generate_id()
            cast.optional['clone'] = old_id

            # save in local git repository
            filename = os.path.join(
                self.repo.working_dir, cast.id+".asciicast")

            with open(filename, "w") as fp:
                cast.save(fp)

            self.repo.index.add([filename])
            self.repo.index.commit("cloning recording '"+cast.id+"'")
            print(cast.id)
        except:
            pass
