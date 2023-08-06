from toto9.gcp_api import GenericGcpApi


class Iam(GenericGcpApi):
    def __init__(self, credentials_path=None, scopes=None):
        self.service_module = 'iam'
        self.service_version = 'v1'
        super(Iam, self).__init__(
            self.service_module,
            self.service_version,
            credentials_path=credentials_path,
            scopes=scopes
        )
        self.iam_service = self.initialized_gcp_service()

    def predefined_roles(self) -> list:
        """List all Predefined Roles
        """
        params = {
            'view': 'FULL'
        }
        try:
            request = self.iam_service.roles().list(**params)
            res = self._execute(request)
        except Exception as e:
            self.logger.error(e)
            return []

        return res['roles']
