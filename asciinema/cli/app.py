import os

from git import Repo
from git.repo.fun import is_git_dir

class AsciinemaCli(object):

    def __init__(self):
        self.dir_home = os.path.join(os.path.expanduser("~"), ".asciinema")
        self.dir_files = os.path.join(self.dir_home, "casts")
        if not is_git_dir(self.dir_files):
            self.cast_repo = Repo.init(self.dir_files, mkdir=True)
            assert not self.cast_repo.bare
        self.cast_repo = Repo(self.dir_files)

    @classmethod
    def run(class_):
        app = class_()
        return app.main()

    def main(self):
        pass

