import requests


class GlobalIdentity:
    def __init__(self, app_key, global_identity_server):
        self.global_identity_server = global_identity_server
        self.app_key = app_key

    def validate_application(self, client_key, raw_data, encrypted_data):

        request = {
            'ApplicationKey': self.app_key,
            'ClientApplicationKey': client_key,
            'RawData': raw_data,
            'EncryptedData': encrypted_data,
        }

        response = requests.post(self.global_identity_server +
                                 '/api/Authorization/ValidateApplication',
                                 data=request)
        return response.json()

    def authenticate_user(self, email, password):
        request = {
            'ApplicationKey': self.app_key,
            'Email': email,
            'Password': password
        }

        response = requests.post(self.global_identity_server +
                                 '/api/Authorization/Authenticate',
                                 data=request)
        return response.json()

    def validate_token(self, token):
        request = {
            'ApplicationKey': self.app_key,
            'Token': token,
        }

        response = requests.post(
            self.global_identity_server +
            '/api/Authorization/ValidateToken',
            data=request)
        return response.json()

    def is_user_in_role(self, user_key, roles):
        request = {
            'ApplicationKey': self.app_key,
            'UserKey': user_key,
            'RoleCollection': roles if isinstance(roles, list) else [roles]
        }

        response = requests.post(self.global_identity_server +
                                 '/api/Authorization/IsUserInRole',
                                 data=request)
        return response.json()
