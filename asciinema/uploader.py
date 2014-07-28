import json
import bz2
import platform
import re

from asciinema import __version__
from asciinema.requests_http_adapter import RequestsHttpAdapter


class ResourceNotFoundError(Exception):
    pass


class ServerMaintenanceError(Exception):
    pass


class Uploader(object):
    def __init__(self, api_url, api_token, http_adapter=None):
        self.http_adapter = http_adapter
        if http_adapter is None:
            self.http_adapter = RequestsHttpAdapter()
        self.api_url = api_url
        self.api_token = api_token

    def upload(self, asciicast):
        url = '%s/api/asciicasts' % self.api_url
        files = self._asciicast_files(asciicast)
        headers = self._headers()

        status, headers, body = self.http_adapter.post(
            url, files=files, headers=headers)

        if status == 503:
            raise ServerMaintenanceError()

        if status == 404:
            raise ResourceNotFoundError()

        return body

    def _asciicast_files(self, asciicast):
        class DummyStdout(object):
            """converting from ttyrec format to asciinema format"""
            def __init__(self, recording):
                timing = []
                rdata = []
                for secs, microsecs, data in recording:
                    timing.append("%d.%d %d" % (secs, microsecs, len(data)))
                    rdata.append(data)

                self.timing = "\n".join(timing)
                self.data = "".join(rdata)

        stdout = DummyStdout(asciicast.recording)
        return {
            'asciicast[stdout]': self._stdout_data_file(stdout),
            'asciicast[stdout_timing]': self._stdout_timing_file(stdout),
            'asciicast[meta]': self._meta_file(asciicast)
        }

    def _headers(self):
        return {'User-Agent': self._user_agent()}

    def _stdout_data_file(self, stdout):
        return ('stdout', bz2.compress(stdout.data))

    def _stdout_timing_file(self, stdout):
        return ('stdout.time', bz2.compress(stdout.timing))

    def _meta_file(self, asciicast):
        return ('meta.json', self._meta_json(asciicast))

    def _meta_json(self, asciicast):
        meta_data = asciicast.meta_data
        meta_data['user_token'] = self.api_token

        return json.dumps(meta_data)

    def _user_agent(self):
        os = re.sub('([^-]+)-(.*)', '\\1/\\2', platform.platform())

        return 'asciinema/%s %s/%s %s' % (
            __version__, platform.python_implementation(),
            platform.python_version(), os)
