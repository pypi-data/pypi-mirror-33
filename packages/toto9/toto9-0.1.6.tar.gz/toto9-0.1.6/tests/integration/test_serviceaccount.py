import os
import unittest
import warnings
import random
import string
import googleapiclient.discovery as google_api

from toto9.serviceaccount import ServiceAccount

CHAR_SEED = string.ascii_uppercase + string.ascii_lowercase + string.digits


def random_string(size=4, prefix=''):
    rando = prefix + ''.join(random.choice(CHAR_SEED) for _ in range(size))
    return rando[:size]

# Note: "test01" pattern to ensure tests are run in order (don't delete
# before we update/get)


class TestServiceAccountMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # ignore the requests session open warning -
        # https://github.com/requests/requests/issues/3912
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

        rando_string = random_string().lower()
        cls.sandbox_project_id = os.getenv('GOOGLE_PROJECT_ID')
        cls.service_account_id = 'toto9-{}'.format(rando_string)
        cls.service_account_full_id = '{}@{}.iam.gserviceaccount.com'.format(
            cls.service_account_id, cls.sandbox_project_id)
        cls.service_account_display_name = 'Toto9 Unit Test SA {}'.format(
            rando_string)
        cls.scopes = ['https://www.googleapis.com/auth/cloud-platform']
        cls.sa_service = ServiceAccount()

    def test01_creds(self):
        # check that the GOOGLE_APPLICATION_CREDENTIALS env var is set
        self.assertIsNotNone(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            msg="Make sure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")
        # check that the project id is set
        self.assertIsNotNone(
            self.sandbox_project_id,
            msg="Make sure the GOOGLE_PROJECT_ID environment variable is set.")

    def test02_create_sa(self):
        sa_create = self.sa_service.create(
            self.sandbox_project_id,
            self.service_account_id,
            {'displayName': self.service_account_display_name}
        )
        self.assertIsInstance(sa_create, dict)

    def test03_get(self):
        sa_get = self.sa_service.get(
            self.service_account_full_id
        )
        self.assertIsInstance(sa_get, dict)

    def test04_update(self):
        sa_update = self.sa_service.update_display_name(
            self.service_account_full_id,
            self.service_account_display_name
        )
        self.assertIsInstance(sa_update, dict)

    def test05_passed_creds(self):
        sa = ServiceAccount(
            credentials_path=os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            scopes=self.scopes
        )
        self.assertIsInstance(sa.sa_service, google_api.Resource)

    def test06_list(self):
        sa_list = self.sa_service.list(self.sandbox_project_id)
        self.assertIsInstance(
            sa_list,
            list,
            msg="ServiceAccount.list should return type of list.")

    def test07_delete_sa(self):
        sa_delete = self.sa_service.delete(
            self.service_account_full_id
        )
        self.assertIsInstance(sa_delete, dict)


if __name__ == '__main__':
    #unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
