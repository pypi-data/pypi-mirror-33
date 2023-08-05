from global_identity.global_identity import GlobalIdentity
from unittest import TestCase
from unittest.mock import MagicMock
import requests


class TestGlobalIdentity(TestCase):

    def setUp(self):
        self.global_identity = GlobalIdentity("app_key", "server")

    def test_validate_application(self):
        requests.post = MagicMock()

        self.global_identity.validate_application("client_key",
                                                  "raw_data",
                                                  "encrypted_data")

        expected_data = {
            'EncryptedData': 'encrypted_data',
            'RawData': 'raw_data',
            'ClientApplicationKey': 'client_key',
            'ApplicationKey': 'app_key'
        }

        expected_url = 'server/api/Authorization/ValidateApplication'

        requests.post.assert_called_with(expected_url, data=expected_data)

    def test_authenticate_user(self):
        requests.post = MagicMock()

        self.global_identity.authenticate_user("email", "password")

        expected_data = {
            'Password': 'password',
            'Email': 'email',
            'ApplicationKey': 'app_key'
        }

        expected_url = 'server/api/Authorization/Authenticate'

        requests.post.assert_called_with(expected_url, data=expected_data)

    def test_validate_token(self):
        requests.post = MagicMock()

        self.global_identity.validate_token("token")

        expected_data = {'Token': 'token', 'ApplicationKey': 'app_key'}

        expected_url = 'server/api/Authorization/ValidateToken'

        requests.post.assert_called_with(expected_url, data=expected_data)

    def test_is_user_in_role(self):
        requests.post = MagicMock()

        self.global_identity.is_user_in_role("user_key", "roles")

        expected_data = {
            'UserKey': 'user_key',
            'ApplicationKey': 'app_key',
            'RoleCollection': ['roles']
        }

        expected_url = 'server/api/Authorization/IsUserInRole'

        requests.post.assert_called_with(expected_url, data=expected_data)

        self.global_identity.is_user_in_role("user_key", ["roles"])

        expected_data = {
            'UserKey': 'user_key',
            'ApplicationKey': 'app_key',
            'RoleCollection': ['roles']
        }

        requests.post.assert_called_with(expected_url, data=expected_data)
