import functools
import json
import datetime
import time

from git import Blob, Commit

class ListCommand(object):
    def __init__(self, repo):
        self.repo = repo

    def _timesince(self, when):
        # convert when to datetime
        if type(when) == int:
            when = datetime.datetime.utcfromtimestamp(when)
        else:
            when = datetime.datetime(*when[:6])

        # humanize output
        now = datetime.datetime.utcnow()
        difference = now - when
        if difference < datetime.timedelta(minutes=2):
            return "%s seconds ago" % difference.seconds
        elif difference < datetime.timedelta(hours=2):
            return "%s minutes ago" % (difference.seconds / 60)
        elif difference < datetime.timedelta(days=2):
            return "%s hours ago" % (difference.days * 24 + difference.seconds / 3600)
        else:
            return time.strftime("%c", when.timetuple())

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

            commit_meta = Commit.iter_items(self.repo, "HEAD",
                paths=meta_blob.path, max_count=1).next()
            commit_data = Commit.iter_items(self.repo, "HEAD",
                paths=data_blob.path, max_count=1).next()

            date = commit_data.committed_date
            if commit_meta.committed_date > commit_data.committed_date:
                date = commit_meta.committed_date

            print "%s [%02d:%02d] %s (%s)" % (
                id, mins, secs, title, self._timesince(date))

