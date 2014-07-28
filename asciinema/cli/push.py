import sys
import functools
import getopt

from git import Blob
from asciinema.asciicast import Asciicast
from asciinema.cli.config import Config
from asciinema.uploader import Uploader
from asciinema.uploader import ServerMaintenanceError
from asciinema.uploader import ResourceNotFoundError


class CastNotFound(Exception):
    pass


class PushCommand(object):
    def __init__(self, repo, arguments=[]):
        try:
            opts, commands = getopt.getopt(arguments, "u:t:qh", ['help'])
        except getopt.error as msg:
            self._help(msg)

        config = Config()

        self.repo = repo
        self.quiet = False
        self.api_url = config.api_url
        self.api_token = config.api_token

        # first non-option is the id to push
        if len(commands) == 0:
            self._help("no asciicast id specified")
        self.id = commands[0]

        # parsing arguments
        for opt, arg in opts:
            if opt in ('-h', '--help'):
                self._help()
            elif opt in ('-q'):
                self.quiet = True
            elif opt in ('-u'):
                self.api_url = arg
            elif opt in ('-t'):
                self.api_token = arg

    def _help(self, msg=None):
        if msg is not None:
            print(msg)
            print('')

        HELP_TEXT = """push [-u <url>] [-t <str>] [-q] [-h] <id>

Upload asciicast to remote repository.

Parameters:
    <id>          id from local repository

Optional arguments:
    -u <url>      the API url base
    -t <str>      the API token
    -q            do not print messages (quiet)
    -h            print this help"""
        print(HELP_TEXT)
        sys.exit(1)

    def execute(self):
        def _predicate_file(file, item, depth):
            if depth > 1:
                return False

            if not isinstance(item, Blob):
                return False

            return item.path == file

        if not self.quiet:
            print('~ Uploading...')

        try:
            head = self.repo.active_branch.commit
            files = [x for x in head.tree.traverse(
                predicate=functools.partial(
                    _predicate_file, str(self.id)+".asciicast"
                )
            )]
            if len(files) == 0:
                raise CastNotFound()

            uploader = Uploader(self.api_url, self.api_token)
            cast = Asciicast.load(files[0].data_stream)
            url = cast.upload(uploader)

            if not self.quiet:
                print('~ Upload succeeded: %s' % url)
        except ServerMaintenanceError:
            if not self.quiet:
                print(
                    '~ Upload failed: The server is down for maintenance.'
                    ' Try again in a minute.')
        except ResourceNotFoundError:
            if not self.quiet:
                print(
                    '~ Upload failed: Your client version is no longer '
                    'supported. Please upgrade to the lastest version.')
        except CastNotFound:
            if not self.quiet:
                print('~ Upload failed: asciicast could not be found')
