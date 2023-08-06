from typing import List, Optional
from toto9.iam import Iam
from copy import deepcopy
import googleapiclient.discovery


class ServiceAccount(Iam):
    def __init__(self, credentials_path: str=None, scopes: List=None) -> None:
        super(ServiceAccount, self).__init__(
            credentials_path=credentials_path,
            scopes=scopes
        )
        self.sa_service: googleapiclient.discovery.Resource = self.iam_service.projects().serviceAccounts()
        self.page_size: int = 100

    def _full_project_id(self, project_id: str) -> str:
        """Returns a properly formatted project ID"""
        return "projects/{}".format(project_id)

    def _full_sa_resource_name(self, service_account_id: str, project_id: Optional[str] = '-') -> str:
        """Returns a fully qualified service account name"""
        return "projects/{}/serviceAccounts/{}".format(
            project_id, service_account_id)

    def list(self, project_id: str) -> List:
        """List Service Accounts created for a given project ID
        Args:
            project_id: The GCP Project ID (e.g. foo-bar-1234)
        """
        full_project_id: str = self._full_project_id(project_id)
        request: googleapiclient.discovery.Request = self.sa_service.list(name=full_project_id, pageSize=self.page_size)
        sa_list: List = []

        self.logger.debug(f'listing service accounts for project {full_project_id}')

        while request is not None:
            service_accounts: dict = self._execute(request)
            sa_list += service_accounts.get('accounts', [])
            request = self.sa_service.list_next(request, service_accounts)

        return sa_list

    def create(self,
               project_id: str,
               service_acct_id: str,
               opts: dict) -> dict:
        """Create a Service Account within a given project
        Args:
            project_id: Project ID
            service_acct_id: Desired ID for Service Account
            opts: Dictionary with optional values:
                displayName (str): The display name for Service Account
                name (str): Formatted as `projects/{PROJECT_ID}/serviceAccounts/{ACCOUNT}`
        """
        full_project_id: str = self._full_project_id(project_id)
        req_body: dict = {
            'serviceAccount': {},
            'accountId': service_acct_id
        }
        req_body['serviceAccount'].update(opts)
        self.logger.debug(f'create service account {service_acct_id} in project {project_id}')
        resp: dict = self._execute(self.sa_service.create(
            name=full_project_id,
            body=req_body))

        return resp

    def delete(self, service_account_id: str, project_id: Optional[str]=None) -> dict:
        """Delete a specified service account
        Args:
            service_account_id: email address or ID of service account to delete
        """
        self.logger.debug(f'delete service account {service_account_id} in project {project_id}')
        resp: dict = self._execute(
            self.sa_service.delete(
                name=self._full_sa_resource_name(service_account_id, project_id=project_id)
            )
        )
        return resp

    def update_display_name(self, service_account_id: str, display_name: str) -> dict:
        """Update the display name for a specified service account
            service_account_id: email address or ID of service account to delete
            display_name: desired display name for service account
        """
        etag: str = self.get(service_account_id)['etag']
        self.logger.debug(f'update name for service account {service_account_id}')
        resp: dict = self._execute(self.sa_service.update(
            name=self._full_sa_resource_name(service_account_id),
            body={
                'displayName': display_name,
                'etag': etag
            }
        ))
        return resp

    def get(self, service_account_id: str) -> dict:
        """Get details about a specified service account
        Args:
            service_account_id: email address or ID of service account to delete
        """
        self.logger.debug(f'get service account {service_account_id}')
        resp: dict = self._execute(self.sa_service.get(
            name=self._full_sa_resource_name(service_account_id)
        ))
        return resp

    def get_iam_policy(self, service_account_id: str) -> dict:
        """Get iam policies for a specified service account
        Args:
            service_account_id: email address or ID of service account
        """
        self.logger.debug(f'get iam policy for service account {service_account_id}')
        resp: dict = self._execute(self.sa_service.getIamPolicy(
            resource=self._full_sa_resource_name(service_account_id)
        ))
        return resp

    def set_iam_policy(self, service_account_id: str, policy: dict) -> dict:
        """Get iam policies for a specified service account
        Args:
            service_account_id: email address or ID of service account
        """
        req_body: dict = {"policy": policy}
        self.logger.debug(f'set iam policy for service account {service_account_id}\npolicy: {policy}')
        resp: dict = self._execute(self.sa_service.setIamPolicy(
            resource=self._full_sa_resource_name(service_account_id), body=req_body))
        return resp

    def add_iam_policy_binding(self, service_account_id: str, member: str, role: List) -> dict:
        """Add policy Binding to given service account
        Args:
            service_account_id: Service Account ID (full email)
            member: member ID, member id must be prefixed with one of user: serviceAccount: group:
            role: list of roles to be added ex: ['roles/spanner.admin']
        """
        # check role in role list is valid
        # check member in supported format
        if not self.valid_resource_member(member):
            raise ValueError('member "{member}" is not a valid resource member ({self.member_prefix})')

        roles: List = deepcopy(role)
        policy: dict = self.get_iam_policy(service_account_id)

        current_policy: dict = deepcopy(policy)
        bindings: List = current_policy.get('bindings', [])
        for binding in bindings:
            if binding['role'] in roles and (member not in binding['members']):
                binding['members'].append(member)
                roles.remove(binding['role'])

        # add additional roles that is not in current bindings
        for role in roles:
            new_binding: dict = {
                'role': role,
                'members': [member]
            }
            bindings.append(new_binding)
        if 'bindings' not in current_policy.keys():
            current_policy['bindings'] = bindings

        self.logger.debug(f'add iam policy binding for member {member} service account {service_account_id}\nrole: {role}')

        resp: dict = self.set_iam_policy(service_account_id, current_policy)
        return resp

    def remove_iam_policy_binding(self, service_account_id: str, member: str, role: List) -> dict:
        """Remove policy Binding from given service account
        Args:
            service_account_id: Service AccountID (full email)
            member: member ID, member id must be prefixed with one of user: serviceAccount: group:
            role: list of roles to be removed ex: ['roles/iam.serviceAccountKeyAdmin']
        """
        # check member in supported format
        if not self.valid_resource_member(member):
            raise ValueError('member "{member}" is not a valid resource member ({self.member_prefix})')

        roles: List = deepcopy(role)
        policy: dict = self.get_iam_policy(service_account_id)
        current_policy: dict = deepcopy(policy)
        bindings: List = current_policy.get('bindings', [])
        for binding in bindings:
            if roles ==[] and (member in binding['members']):
                binding['members'].remove(member)
            elif binding['role'] in roles and (member in binding['members']):
                binding['members'].remove(member)
            if not binding['members']:
                # no more member, remove this binding
                bindings.remove(binding)

        self.logger.debug(f'remove iam policy binding for member {member} service account {service_account_id}\nrole: {role}')

        resp: dict = self.set_iam_policy(service_account_id, current_policy)
        return resp
