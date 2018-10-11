import unittest

from botocore.stub import Stubber
from mock import patch
from envs import env

from warrant import Cognito, UserObj, GroupObj, TokenVerificationException
from warrant.aws_srp import AWSSRP


def _mock_get_params(_):
    return {'USERNAME': 'bob', 'SRP_A': 'srp'}


class UserObjTestCase(unittest.TestCase):

    def setUp(self):
        if env('USE_CLIENT_SECRET', 'False') == 'True':
            self.app_id = env('COGNITO_APP_WITH_SECRET_ID')
        else:
            self.app_id = env('COGNITO_APP_ID')
        self.cognito_user_pool_id = env('COGNITO_USER_POOL_ID', 'us-east-1_123456789')
        self.username = env('COGNITO_TEST_USERNAME')

        self.user = Cognito(user_pool_id=self.cognito_user_pool_id,
                            client_id=self.app_id,
                            username=self.username)

        self.user_metadata = {
            'user_status': 'CONFIRMED',
            'username': 'bjones',
        }
        self.user_info = [
            {'Name': 'name', 'Value': 'Brian Jones'},
            {'Name': 'given_name', 'Value': 'Brian'},
            {'Name': 'birthdate', 'Value': '12/7/1980'}
        ]

    def test_init(self):
        u = UserObj('bjones', self.user_info, self.user, self.user_metadata)
        self.assertEqual(u.pk, self.user_metadata.get('username'))
        self.assertEqual(u.name, self.user_info[0].get('Value'))
        self.assertEqual(u.user_status, self.user_metadata.get('user_status'))


class GroupObjTestCase(unittest.TestCase):

    def setUp(self):
        if env('USE_CLIENT_SECRET', 'False') == 'True':
            self.app_id = env('COGNITO_APP_WITH_SECRET_ID')
        else:
            self.app_id = env('COGNITO_APP_ID')
        self.cognito_user_pool_id = env('COGNITO_USER_POOL_ID', 'us-east-1_123456789')
        self.group_data = {'GroupName': 'test_group', 'Precedence': 1}
        self.cognito_obj = Cognito(user_pool_id=self.cognito_user_pool_id,
                                   client_id=self.app_id)

    def test_init(self):
        group = GroupObj(group_data=self.group_data, cognito_obj=self.cognito_obj)
        self.assertEqual(group.group_name, 'test_group')
        self.assertEqual(group.precedence, 1)

#
# class CognitoAuthTestCase(unittest.TestCase):
#
#     def setUp(self):
#         if env('USE_CLIENT_SECRET') == 'True':
#             self.app_id = env('COGNITO_APP_WITH_SECRET_ID')
#             self.client_secret = env('COGNITO_CLIENT_SECRET')
#         else:
#             self.app_id = env('COGNITO_APP_ID')
#             self.client_secret = None
#         self.cognito_user_pool_id = env('COGNITO_USER_POOL_ID', 'us-east-1_123456789')
#         self.username = env('COGNITO_TEST_USERNAME')
#         self.password = env('COGNITO_TEST_PASSWORD')
#         self.user = Cognito(self.cognito_user_pool_id,self.app_id,
#                             username=self.username,
#                             client_secret=self.client_secret)
#
#     def test_authenticate(self):
#         self.user.authenticate(self.password)
#         self.assertNotEqual(self.user.access_token,None)
#         self.assertNotEqual(self.user.id_token, None)
#         self.assertNotEqual(self.user.refresh_token, None)
#
#     def test_verify_token(self):
#         self.user.authenticate(self.password)
#         bad_access_token = '{}wrong'.format(self.user.access_token)
#
#         with self.assertRaises(TokenVerificationException) as vm:
#             self.user.verify_token(bad_access_token, 'access_token', 'access')
#
#     # def test_logout(self):
#     #     self.user.authenticate(self.password)
#     #     self.user.logout()
#     #     self.assertEqual(self.user.id_token,None)
#     #     self.assertEqual(self.user.refresh_token,None)
#     #     self.assertEqual(self.user.access_token,None)
#
#     @patch('warrant.Cognito', autospec=True)
#     def test_register(self, cognito_user):
#         u = cognito_user(self.cognito_user_pool_id, self.app_id,
#                          username=self.username)
#         u.add_base_attributes(
#             given_name='Brian', family_name='Jones',
#             name='Brian Jones', email='bjones39@capless.io',
#             phone_number='+19194894555', gender='Male',
#             preferred_username='billyocean')
#         res = u.register('sampleuser', 'sample4#Password')
#
#         #TODO: Write assumptions
#
#     def test_renew_tokens(self):
#         self.user.authenticate(self.password)
#         self.user.renew_access_token()
#
#     @patch('warrant.Cognito', autospec=True)
#     def test_update_profile(self,cognito_user):
#         u = cognito_user(self.cognito_user_pool_id, self.app_id,
#                          username=self.username)
#         u.authenticate(self.password)
#         u.update_profile({'given_name':'Jenkins'})
#
#     def test_admin_get_user(self):
#         u = self.user.admin_get_user()
#         self.assertEqual(u.pk,self.username)
#
#     def test_check_token(self):
#         self.user.authenticate(self.password)
#         self.assertFalse(self.user.check_token())
#
#     @patch('warrant.Cognito', autospec=True)
#     def test_validate_verification(self,cognito_user):
#         u = cognito_user(self.cognito_user_pool_id,self.app_id,
#                          username=self.username)
#         u.validate_verification('4321')
#
#     @patch('warrant.Cognito', autospec=True)
#     def test_confirm_forgot_password(self,cognito_user):
#         u = cognito_user(self.cognito_user_pool_id, self.app_id,
#                          username=self.username)
#         u.confirm_forgot_password('4553','samplepassword')
#         with self.assertRaises(TypeError) as vm:
#             u.confirm_forgot_password(self.password)
#
#     @patch('warrant.Cognito', autospec=True)
#     def test_change_password(self,cognito_user):
#         u = cognito_user(self.cognito_user_pool_id, self.app_id,
#                          username=self.username)
#         u.authenticate(self.password)
#         u.change_password(self.password,'crazypassword$45DOG')
#
#         with self.assertRaises(TypeError) as vm:
#             self.user.change_password(self.password)
#
#     def test_set_attributes(self):
#         u = Cognito(self.cognito_user_pool_id,self.app_id)
#         u._set_attributes({
#                 'ResponseMetadata':{
#                     'HTTPStatusCode':200
#                 }
#         },
#             {
#                 'somerandom':'attribute'
#             }
#         )
#         self.assertEqual(u.somerandom,'attribute')
#
#     def test_admin_authenticate(self):
#
#         self.user.admin_authenticate(self.password)
#         self.assertNotEqual(self.user.access_token,None)
#         self.assertNotEqual(self.user.id_token, None)
#         self.assertNotEqual(self.user.refresh_token, None)


class AWSSRPTestCase(unittest.TestCase):

    def setUp(self):
        if env('USE_CLIENT_SECRET') == 'True':
            self.client_secret = env('COGNITO_CLIENT_SECRET')
            self.app_id = env('COGNITO_APP_WITH_SECRET_ID', 'app')
        else:
            self.app_id = env('COGNITO_APP_ID', 'app')
            self.client_secret = None
        self.cognito_user_pool_id = env('COGNITO_USER_POOL_ID', 'us-east-1_123456789')
        self.username = env('COGNITO_TEST_USERNAME')
        self.password = env('COGNITO_TEST_PASSWORD')
        self.aws = AWSSRP(username=self.username,
                          password=self.password,
                          pool_region='us-east-1',
                          pool_id=self.cognito_user_pool_id,
                          client_id=self.app_id,
                          client_secret=self.client_secret)

        self.stub = Stubber(self.aws.client)

        # By the stubber nature, we need to add the sequence
        # of calls for the AWS SRP auth to test the whole process
        self.stub.add_response(method='initiate_auth',
                               service_response={
                                   'ChallengeName': 'PASSWORD_VERIFIER',
                                   'ChallengeParameters': {}
                               },
                               expected_params={
                                   'AuthFlow': 'USER_SRP_AUTH',
                                   'AuthParameters': _mock_get_params(None),
                                   'ClientId': self.app_id
                               })

        self.stub.add_response(method='respond_to_auth_challenge',
                               service_response={
                                   'AuthenticationResult': {
                                       'IdToken': 'dummy_token',
                                       'AccessToken': 'dummy_token',
                                       'RefreshToken': 'dummy_token'
                                   }
                               },
                               expected_params={
                                   'ClientId': self.app_id,
                                   'ChallengeName': 'PASSWORD_VERIFIER',
                                   'ChallengeResponses': {}
                               })

    def tearDown(self):
        del self.aws

    @patch('warrant.aws_srp.AWSSRP.get_auth_params', _mock_get_params)
    @patch('warrant.aws_srp.AWSSRP.process_challenge', return_value={})
    def test_authenticate_user(self, _):
        with self.stub:
            tokens = self.aws.authenticate_user()
            self.assertTrue('IdToken' in tokens['AuthenticationResult'])
            self.assertTrue('AccessToken' in tokens['AuthenticationResult'])
            self.assertTrue('RefreshToken' in tokens['AuthenticationResult'])
            self.stub.assert_no_pending_responses()


if __name__ == '__main__':
    unittest.main()
