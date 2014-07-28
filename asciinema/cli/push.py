import functools

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
        config = Config()

        self.repo = repo
        self.quiet = False
        self.api_url = config.api_url
        self.api_token = config.api_token
        self.id = arguments[0]


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
                print('~ Upload failed: The server is down for maintenance.' + \
                    ' Try again in a minute.')
        except ResourceNotFoundError:
            if not self.quiet:
                print('~ Upload failed: Your client version is no longer ' + \
                    'supported. Please upgrade to the lastest version.')
        except CastNotFound:
            if not self.quiet:
                print('~ Upload failed: asciicast could not be found')

