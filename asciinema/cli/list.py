import functools
import json

from git import Blob


class ListCommand(object):
    def __init__(self, repo):
        self.repo = repo

    def doit(self, argv=[]):
        def _predicate_ttyrec(item, depth):
            """find all ttyrec files in local git repository"""
            if depth > 1:
                return False

            if not isinstance(item, Blob):
                return False

            return item.path.endswith(".ttyrec")

        def _predicate_meta(filename, item, depth):
            """find a meta file with a specific name"""
            if depth > 1:
                return False

            if not isinstance(item, Blob):
                return False

            return item.path == filename

        head = self.repo.commit()
        for data_blob in head.tree.traverse(predicate=_predicate_ttyrec):
            id,_ = data_blob.path.split(".")
            meta_blob = head.tree.traverse(
                predicate=functools.partial(_predicate_meta,id+".meta")).next()

            # no metadata found
            if meta_blob is None:
                continue

            meta_data = json.load(meta_blob.data_stream)
            mins, secs = meta_data['duration'] // 60.0, meta_data['duration'] % 60
            title = "<no title>"
            if meta_data['title'] is not None:
                title = "\"%s\"" % meta_data['title']

            print "%s [%02d:%02d] %s" % (id, mins, secs, title)

