import functools
import json
import datetime
import time

from git import Blob, Commit
from asciinema.asciicast import Asciicast

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
        def _predicate_cast(item, depth):
            """find all asciicast files in local git repository"""
            if depth > 1:
                return False

            if not isinstance(item, Blob):
                return False

            return item.path.endswith(".asciicast")

        try:
            head = self.repo.active_branch.commit
        except ValueError:
            # repository has currently no content (initial)
            return

        for data_blob in head.tree.traverse(predicate=_predicate_cast):
            id,_ = data_blob.path.split(".")
            cast = Asciicast.load(data_blob.data_stream)

            mins, secs = cast.duration // 60.0, cast.duration % 60
            title = "<no title>"
            if cast.title is not None:
                title = "\"%s\"" % cast.title

            commit_data = Commit.iter_items(self.repo, "HEAD",
                paths=data_blob.path, max_count=1).next()

            print "%s [%02d:%02d] %s (%s)" % (
                id, mins, secs, title,
                self._timesince(commit_data.committed_date)
            )

