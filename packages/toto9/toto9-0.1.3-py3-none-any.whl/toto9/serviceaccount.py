from typing import List
from toto9.iam import Iam

class ServiceAccount(Iam):
    def __init__(self, credentials_path: str=None, scopes: List=None):
        super(ServiceAccount, self).__init__(
            credentials_path=credentials_path,
            scopes=scopes
        )
        self.sa_service = self.iam_service.projects().serviceAccounts()
        self.page_size = 100

    def _full_project_id(self, project_id: str) -> str:
        """Returns a properly formatted project ID"""
        return "projects/{}".format(project_id)

    def _full_sa_resource_name(self, service_account_id: str) -> str:
        """Returns a fully qualified service account name"""
        return "projects/-/serviceAccounts/{}".format(service_account_id)

    def list(self, project_id: str) -> dict:
        """List Service Accounts created for a given project ID
        Args:
            project_id: The GCP Project ID (e.g. foo-bar-1234)
        """
        full_project_id = self._full_project_id(project_id)
        request = self.sa_service.list(name=full_project_id, pageSize=self.page_size)
        sa_list = []

        while request is not None:
            service_accounts = self._execute(request)
            sa_list.append(service_accounts)
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
        full_project_id = self._full_project_id(project_id)
        req_body = {
            'serviceAccount': {},
            'accountId': service_acct_id
        }
        req_body['serviceAccount'].update(opts)
        resp = self._execute(self.sa_service.create(
            name=full_project_id,
            body=req_body))

        return resp

    def delete(self, service_account_id: str) -> dict:
        """Delete a specified service account
        Args:
            service_account_id: email address or ID of service account to delete
        """
        resp = self._execute(
            self.sa_service.delete(
                name=self._full_sa_resource_name(service_account_id)
            )
        )
        return resp


    def update_display_name(self, service_account_id: str, display_name: str) -> dict:
        """Update the display name for a specified service account
            service_account_id: email address or ID of service account to delete
            display_name: desired display name for service account
        """
        etag = self.get(service_account_id)['etag']
        resp = self._execute(self.sa_service.update(
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
        resp = self._execute(self.sa_service.get(
            name=self._full_sa_resource_name(service_account_id)
        ))
        return resp
