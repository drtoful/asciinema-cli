import os

from git import Repo
from git.repo.fun import is_git_dir
from asciinema.asciicast import Asciicast

class AsciinemaCli(object):

    def __init__(self):
        self.dir_home = os.path.join(os.path.expanduser("~"), ".asciinema")
        self.dir_files = os.path.join(self.dir_home, "casts")
        if not is_git_dir(self.dir_files):
            self.cast_repo = Repo.init(self.dir_files, mkdir=True)
            assert not self.cast_repo.bare
        self.cast_repo = Repo(self.dir_files)

    def _save_local(self, cast):
        ttyrec_file = os.path.join(self.dir_files, cast.id+".ttyrec")
        meta_file = os.path.join(self.dir_files, cast.id+".meta")

        with open(ttyrec_file, "w") as fp:
            print >>fp, cast.as_ttyrec()

        with open(meta_file, "w") as fp:
            print >>fp, cast.meta_data

        self.cast_repo.index.add([ttyrec_file, meta_file])
        self.cast_repo.index.commit("update recording '"+cast.id+"'")


    @classmethod
    def run(class_):
        app = class_()
        return app.main()

    def main(self):
        title = None


        cast = Asciicast(title)
        cast.record()
        self._save_local(cast)


