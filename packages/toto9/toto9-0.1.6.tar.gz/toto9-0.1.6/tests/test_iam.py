import os
import unittest
import warnings
import string
import googleapiclient.discovery as google_api

from toto9.iam import Iam

CHAR_SEED = string.ascii_uppercase + string.ascii_lowercase + string.digits


# Note: "test01" pattern to ensure tests are run in order (don't delete
# before we update/get)


class TestIamMethods(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        # ignore the requests session open warning -
        # https://github.com/requests/requests/issues/3912
        warnings.filterwarnings(
            "ignore",
            category=ResourceWarning,
            message="unclosed.*<ssl.SSLSocket.*>")

        cls.iam_service = Iam()

    def test01_creds(self):
        # check that the GOOGLE_APPLICATION_CREDENTIALS env var is set
        self.assertIsNotNone(
            os.getenv('GOOGLE_APPLICATION_CREDENTIALS'),
            msg="Make sure the GOOGLE_APPLICATION_CREDENTIALS environment variable is set.")

    def test02_predefined_roles(self):
        roles = self.iam_service.predefined_roles()
        self.assertIsInstance(roles, dict)
        self.assertIn('roles', roles.keys())
        self.assertNotEqual(roles['roles'], [])


if __name__ == '__main__':
    unittest.TestLoader.sortTestMethodsUsing = None
    unittest.main()
