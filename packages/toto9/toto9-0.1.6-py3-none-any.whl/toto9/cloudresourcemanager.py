from typing import List, Dict, Any
import googleapiclient.discovery
from toto9.gcp_api import GenericGcpApi
from copy import deepcopy


class CloudResourceManager(GenericGcpApi):
    def __init__(self, credentials_path=None, scopes=None) -> None:
        self.service_module: str = 'cloudresourcemanager'
        self.service_version: str = 'v1'

        super(CloudResourceManager, self).__init__(
            self.service_module,
            self.service_version,
            credentials_path=credentials_path,
            scopes=scopes
        )
        self.crm_service: googleapiclient.discovery.Resource = self.initialized_gcp_service()

    def organization_get(self, org_id: str) -> Dict:
        """Get Organization Info for given Organization ID
        Args:
            org_id: Organization ID
        """
        params: Dict[str, Any] = {
            'name': org_id,
            'fields': None
        }
        request: googleapiclient.discovery.Request = self.crm_service.organizations().get(**params)
        res: Dict = self._execute(request)

        return res

    def projects_list(self) -> List:
        """List All Projects
        """
        project_list: List = []
        request: googleapiclient.discovery.Request = self.crm_service.projects().list(pageSize=100)
        while request is not None:
            res: Dict = self._execute(request)
            project_list += res.get('projects', [])
            request = self.crm_service.projects().list_next(request, res)

        return project_list

    def project_get(self, project_id: str) -> Dict:
        """Get Project Info for given Project ID
        Args:
            project_id: Project ID
        """
        params: Dict[str, Any] = {
            'projectId': project_id,
            'fields': None
        }

        request: googleapiclient.discovery.Resource = self.crm_service.projects().get(**params)
        res: Dict = self._execute(request)

        return res

    def get_project_iam_policy(self, project_id: str) -> Dict:
        """Get Project IAM Policies for given Project ID
        Args:
            project_id: Project ID
        """
        params: Dict[str, Any] = {
            'resource': project_id,
            'fields': None
        }

        request: googleapiclient.discovery.Request = self.crm_service.projects().getIamPolicy(**params)
        res: Dict = self._execute(request)

        return res

    def set_project_iam_policy(self, project_id: str, policy: Dict) -> Dict:
        """Set Project IAM Policies for given Project ID
        Args:
            project_id: Project ID
            policy: Policy dict contanint bindings and etag
        """
        params: Dict[str, Any] = {
            'resource': project_id,
            'body': {'policy': policy}
        }

        request: googleapiclient.discovery.Request = self.crm_service.projects().setIamPolicy(**params)
        res: Dict = self._execute(request)

        return res

    def add_iam_policy_binding(self, project_id: str, member: str, role: list) -> Dict:
        """Add IAM policy Binding to given Project
        Args:
            project_id: Project ID
            member: member ID, member id must be prefixed with one of user: serviceAccount: group:
            role: list of roles to be added ex: ['roles/spanner.admin']
        """
        # check role in role list is valid
        # check member in supported format
        member_prefix: List = ['user', 'serviceAccount', 'group']
        if not member.split(':')[0] in member_prefix:
            return {'error': 'unsupported member format'}

        roles: List = deepcopy(role)
        policy: Dict = self.get_project_iam_policy(project_id)
        current_policy = deepcopy(policy)
        bindings: List = current_policy.get('bindings', [])
        for binding in bindings:
            if binding['role'] in roles and (member not in binding['members']):
                binding['members'].append(member)
                roles.remove(binding['role'])

        # add additional roles that is not in current bindings
        for role in roles:
            new_binding: Dict[str, Any] = {
                'role': role,
                'members': [member]
            }
            bindings.append(new_binding)
        if 'bindings' not in current_policy.keys():
            current_policy['bindings'] = bindings

        resp: Dict = self.set_project_iam_policy(project_id, current_policy)
        return resp

    def remove_iam_policy_binding(self, project_id: str, member: str, role: list) -> Dict:
        """Remove IAM policy Binding to given Project
        Args:
            project_id: Project ID
            member: member ID, member id must be prefixed with one of user: serviceAccount: group:
            role: list of roles to be added ex: ['roles/spanner.admin']
        """
        # TODO check role in role list is valid
        # check member in supported format
        member_prefix: List = ['user', 'serviceAccount', 'group']
        if not member.split(':')[0] in member_prefix:
            return {'error': 'unsupported member format'}

        roles: List = deepcopy(role)
        policy: Dict = self.get_project_iam_policy(project_id)
        current_policy: Dict = deepcopy(policy)
        bindings: List = current_policy.get('bindings', [])
        for binding in bindings:
            if roles == [] and (member in binding['members']):
                binding['members'].remove(member)
            elif binding['role'] in roles and (member in binding['members']):
                binding['members'].remove(member)
            if not binding['members']:
                # no more member, remove this binding
                bindings.remove(binding)

        resp: Dict = self.set_project_iam_policy(project_id, current_policy)
        return resp

    def get_org_iam_policy(self, org_id: str) -> Dict:
        """Get Organization IAM Policies for given Organization ID
        Args:
            org_id: Organization ID
        """
        params: Dict[str, Any] = {
            'resource': 'organizations/{}'.format(org_id),
            'fields': None
        }

        request: googleapiclient.discovery.Request = self.crm_service.organizations().getIamPolicy(**params)
        res: Dict = self._execute(request)

        return res
