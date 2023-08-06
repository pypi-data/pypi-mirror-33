from typing import List
from toto9.gcp_api import GenericGcpApi
from toto9.errors import GcpApiExecutionError


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
        self.member_prefix = ['user', 'serviceAccount', 'group']
        self.page_size = 100

    def predefined_roles(self) -> list:
        """List all Predefined Roles
        """
        params = {
            'view': 'FULL'
        }
        request = self.iam_service.roles().list(**params)
        res = self._execute(request)

        return res

    def get_project_role(self, name: str) -> dict:
        """Get a Role definition
        """
        params = {
            'name': name
        }
        request = self.iam_service.projects().roles().get(**params)
        res = self._execute(request)

        return res

    def create_role(self, project_id: str, role: dict) -> dict:
        """Create Custom Roles for a project
        """
        params = {
            'parent': 'projects/{}'.format(project_id),
            'body': role
        }
        request = self.iam_service.projects().roles().create(**params)
        res = self._execute(request)

        return res

    def patch_role(self, name: str, body: dict) -> dict:
        """Patch Custom Roles for a project
        """
        params = {
            'name': name,
            'body': body
        }
        request = self.iam_service.projects().roles().patch(**params)
        res = self._execute(request)

        return res

    def delete_role(self, name: str) -> dict:
        """Delete Custom Roles for a project
        """
        params = {
            'name': name,
        }
        request = self.iam_service.projects().roles().delete(**params)
        res = self._execute(request)

        return res

    def custom_roles(self, project_id: str) -> list:
        """List Custom Roles for a project
        """
        params = {
            'parent': 'projects/{}'.format(project_id),
            'view': 'FULL'
        }
        request = self.iam_service.projects().roles().list(**params)
        res = self._execute(request)

        return res

    def custom_org_roles(self, org_id: str) -> list:
        """List Custom Roles for an org
        """
        params = {
            'parent': 'organizations/{}'.format(org_id),
            'view': 'FULL'
        }
        request = self.iam_service.organizations().roles().list(**params)
        res = self._execute(request)

        return res

    def valid_resource_member(self, member) -> bool:
        return member.split(':')[0] in self.member_prefix

    def get_testable_permissions(self, resource_id: str) -> List:
        """Get Testable permissions
        """
        full_resource_name = f'//cloudresourcemanager.googleapis.com/{resource_id}'
        params = {
            'body': {
            'fullResourceName': full_resource_name,
            'pageSize': self.page_size
            }
        }
        request: googleapiclient.discovery.Request = self.iam_service.permissions().queryTestablePermissions(**params)
        permission_list: List = []

        self.logger.debug(f'listing testable permissions for resource {resource_id}')

        while request is not None:
            permissions: dict = self._execute(request)
            permission_list += permissions.get('permissions', [])
            if not permissions.get('nextPageToken'):
                break
            params['body']['pageToken'] = permissions.get('nextPageToken')
            request: googleapiclient.discovery.Request = self.iam_service.permissions().queryTestablePermissions(**params)

        self.logger.debug(permission_list)
        return permission_list
