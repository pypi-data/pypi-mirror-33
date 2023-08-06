"""TODO docs
"""

import io
import json
from datetime import datetime, timezone

from klein               import Klein
from twisted.logger      import Logger
from werkzeug.exceptions import NotFound, BadRequest

class CsvTsdb():
    """TODO docs
    """
    GET_BYTES = 10*1024  # how many bytes to truncate to in GET requests

    app = Klein()

    def __init__(self, filename):
        self.log      = Logger()
        self.filename = filename
        self.log.info("CsvTsdb on file {file}", file=self.filename)

    @app.route('/', methods=['POST'])
    def save(self, request):
        try:
            data = request.content.read().decode('utf-8').strip()
            try:
                label, value = data.rsplit(maxsplit=1)
                value = float(value)
            except ValueError as e:  # didn't parse as "label something 47" => assume it is just a label without number
                label, value = data, 1.0  # no value => value 1 (for ease of use)
            if '"' in label: raise ValueError('label may not contain a " (double quote)')
            if ',' in label: raise ValueError('label may not contain a , (comma)')
        except ValueError as e:
            raise BadRequest(e) from e

        ts = datetime.now(timezone.utc).replace(microsecond=0).isoformat()
        csv_line = '{}, "{}", {}\n'.format(ts, label, value)
        with open(self.filename, 'a') as f:
            f.write(csv_line)

        request.setResponseCode(204)
        return None

    @app.route('/', methods=['GET'])
    def get(self, request):
        # TODO this should eventually do something else -- some more advanced querying
        try:
            with open(self.filename, 'r') as f:
                f.seek(0, io.SEEK_END)
                end = f.tell()
                beg = max(0, end - self.GET_BYTES)
                f.seek(beg, io.SEEK_SET)
                f.readline() # eat stuff until next newline
                return f.read()  # for now this is synchronous because 10kb isn't that much
        except FileNotFoundError:
            return b''

    @app.handle_errors(BadRequest)
    def handle_errors(self, request, failure):
        self.log.warn(str(failure))
        request.setResponseCode(failure.value.code)
        request.setHeader('Content-Type', 'text/plain')
        return failure.getErrorMessage()

    @property
    def resource(self):
        return self.app.resource()
