
class Error(Exception):
    """Base Error"""

class GcpApiExecutionError(Error):
    CUSTOM_ERROR_MESSAGE = (
        'GCP API Error: unable to get {0} from GCP:\n{1}\n{2}')

    def __init__(self, method, e):
        super(GcpApiExecutionError, self).__init__(
            self.CUSTOM_ERROR_MESSAGE.format(
                method, e, e.content.decode('utf-8')))
        self.http_error = e
