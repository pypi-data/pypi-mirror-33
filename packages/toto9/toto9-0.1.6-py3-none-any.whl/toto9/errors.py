
class Error(Exception):
    """Base Error"""


class GcpApiExecutionError(Error):
    CUSTOM_ERROR_MESSAGE = (
        "GCP API Error: unable to get {} from GCP:\n{}\n{}")

    def __init__(self, method, e):
        self.method = method
        self.exception = e
        error_msg = self.CUSTOM_ERROR_MESSAGE.format(
            self.method, self.exception, self.exception.content.decode('utf-8'))
        super(GcpApiExecutionError, self).__init__(
            error_msg)

        self.http_error = e

    @property
    def error_message(self):
        error_msg = self.CUSTOM_ERROR_MESSAGE.format(
            self.method, self.exception, self.exception.content.decode('utf-8'))

        return error_msg
