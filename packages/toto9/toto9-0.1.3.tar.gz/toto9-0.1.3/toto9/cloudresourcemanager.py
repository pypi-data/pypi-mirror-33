from toto9.gcp_api import GenericGcpApi
from copy import deepcopy

class CloudResourceManager(GenericGcpApi):
    def __init__(self, credentials_path=None, scopes=None):
        self.service_module = 'cloudresourcemanager'
        self.service_version = 'v1'
        
        super(CloudResourceManager, self).__init__(
            self.service_module,
            self.service_version,
            credentials_path=credentials_path,
            scopes=scopes
        )
        self.crm_service = self.initialized_gcp_service()

    def organization_get(self, org_id: str) -> dict:
        """Get Organization Info for given Organization ID
        Args:
            org_id: Organization ID
        """
        params = {
            'name': org_id,
            'fields': None
        }
        try:
            request = self.crm_service.organizations().get(**params)
            res = self._execute(request)
        except Exception as e:
            self.logger.error(e)
            return {}
        return res

    def projects_list(self) -> list:
        """List All Projects
        """
        request = self.crm_service.projects().list()
        try:
            res = self._execute(request)
        except Exception as e:
            self.logger.error(e)
            return []
        return res.get('projects', [])

    def project_get(self, project_id: str) -> dict:
        """Get Project Info for given Project ID
        Args:
            project_id: Project ID
        """
        params = {
            'projectId': project_id,
            'fields': None
        }

        try:
            request = self.crm_service.projects().get(**params)
            res = self._execute(request)
        except Exception as e:
            self.logger.error(e)
            return {}
        return res

    def get_project_iam_policies(self, project_id: str) -> dict:
        """Get Project IAM Policies for given Project ID
        Args:
            project_id: Project ID
        """
        params = {
            'resource': project_id,
            'fields': None
        }
        try:
            request = self.crm_service.projects().getIamPolicy(**params)
            res = self._execute(request)
        except Exception as e:
            self.logger.error(e)
            return {}

        return res

    def set_project_iam_policies(self, project_id: str, policy: dict) -> dict:
        """Set Project IAM Policies for given Project ID
        Args:
            project_id: Project ID
            policy: Policy dict contanint bindings and etag
        """
        params = {
            'resource': project_id,
            'body': {'policy': policy}
        }
        try:
            request = self.crm_service.projects().setIamPolicy(**params)
            res = self._execute(request)
        except Exception as e:
            self.logger.error(e)
            return {'error': e}
        #check if binding matches requested binding
        # if match, return success, otherwise raise failure?
        print(res)
        return res

    def add_iam_policy_binding(self, project_id: str, member: str, role: list) -> dict:
        """Add IAM policy Binding to given Project
        Args:
            project_id: Project ID
            member: member ID, member id must be prefixed with one of user: serviceAccount: group:
            role: list of roles to be added ex: ['roles/spanner.admin']
        """
        # check role in role list is valid
        # check member in supported format
        member_prefix = ['user', 'serviceAccount', 'group']
        if not member.split(':')[0] in member_prefix:
            return {'error': 'unsupported member format'}

        roles = deepcopy(role)
        policy = self.get_project_iam_policies(project_id)
        current_policy = deepcopy(policy)
        bindings = current_policy.get('bindings', [])
        for binding in bindings:
            if binding['role'] in roles and (member not in binding['members']):
                binding['members'].append(member)
                roles.remove(binding['role'])

        # add additional roles that is not in current bindings
        for role in roles:
            new_binding = {
                'role': role,
                'members': [member]
            }
            bindings.append(new_binding)

        resp = self.set_project_iam_policies(project_id, current_policy)
        return resp

    def remove_iam_policy_binding(self, project_id: str, member: str, role: list) -> dict:
        """Remove IAM policy Binding to given Project
        Args:
            project_id: Project ID
            member: member ID, member id must be prefixed with one of user: serviceAccount: group:
            role: list of roles to be added ex: ['roles/spanner.admin']
        """
        # TODO check role in role list is valid
        # check member in supported format
        member_prefix = ['user', 'serviceAccount', 'group']
        if not member.split(':')[0] in member_prefix:
            return {'error': 'unsupported member format'}

        roles = deepcopy(role)
        policy = self.get_project_iam_policies(project_id)
        current_policy = deepcopy(policy)
        bindings = current_policy.get('bindings', [])
        for binding in bindings:
            if binding['role'] in roles and (member in binding['members']):
                binding['members'].remove(member)
            if not binding['members']:
                # no more member, remove this binding
                bindings.remove(binding)

        resp = self.set_project_iam_policies(project_id, current_policy)
        return resp

    def get_org_iam_policies(self, org_id: str) -> dict:
        """Get Organization IAM Policies for given Organization ID
        Args:
            org_id: Organization ID
        """
        params = {
            'resource': org_id,
            'fields': None
        }
        try:
            request = self.crm_service.organizations().getIamPolicy(**params)
            res = self._execute(request)
        except Exception as e:
            self.logger.error(e)
            return {}

        return res
