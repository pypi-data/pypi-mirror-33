from google.oauth2 import service_account
import googleapiclient.discovery
from googleapiclient import errors
from httplib2 import HttpLib2Error
from abc import ABC
import errno
import os
import logging

import toto9.retryable_exceptions as retryable_exceptions
import toto9.errors as api_errors
from retrying import retry


class GenericGcpApi(ABC):
    def __init__(self,
                 service,
                 version,
                 credentials_path=None,
                 scopes=None,
                 log_level='DEBUG'
                 ):
        self.__init_logger(log_level)
        self.service_name = service
        self.version = version
        self.scopes = scopes
        self.credentials_path = credentials_path
        self.credentials = None
        self.__init_creds()

    def __init_logger(self, log_level):
        logging.basicConfig(
            level=logging.getLevelName(log_level)
        )
        self.logger = logging.getLogger(__name__)

    def __init_creds(self):
        if self.scopes and self.credentials_path:
            self.logger.debug('using non-default scopes and credentials')
            if not os.path.exists(self.credentials_path):
                self.logger.error('credentials file not found')
                raise FileNotFoundError(
                    errno.ENOENT, os.strerror(
                        errno.ENOENT), self.credentials_path)

            self.credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path, scopes=self.scopes)

    @retry(retry_on_exception=retryable_exceptions.is_retryable_exception,
           wait_exponential_multiplier=1000, wait_exponential_max=10000,
           stop_max_attempt_number=3)
    def _execute(self, request):
        self.logger.debug('making request %s', request.to_json())
        try:
            return request.execute()
        except (errors.HttpError, HttpLib2Error) as e:
            api_exception = api_errors.GcpApiExecutionError(
                request.to_json(), e)
            self.logger.error(api_exception.error_message)
            raise api_exception

    def initialized_gcp_service(self):
        return googleapiclient.discovery.build(
            self.service_name, self.version, credentials=self.credentials)
