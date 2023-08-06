import json, requests, unittest, mock

from impersonator.client import Impersonator

MOCK_TOKEN = 'exampletokencharacters'
MOCK_ERROR = 'example error message'
MOCK_COMMAND_SUCCESS = 'success_cmd'
MOCK_COMMAND_FAILURE = 'failure_cmd'
MOCK_OUTPUT = {
    'code': 0,
    'err': 'error',
    'out': 'output'
}

SUCCESS_CODE = 200
FAILURE_CODE = 400

class MockResponse:
    def __init__(self, text, status_code):
        self.text = text
        self.status_code = status_code

    def json(self):
        return json.loads(self.text)

def mock_post_request(*args, **kwargs):
    if args[0].endswith('/tokens'):
        return MockResponse(MOCK_TOKEN, SUCCESS_CODE)
    elif kwargs['json']['command'] == MOCK_COMMAND_SUCCESS:
        return MockResponse(json.dumps(MOCK_OUTPUT), SUCCESS_CODE)
    elif kwargs['json']['command'] == MOCK_COMMAND_FAILURE:
        return MockResponse(MOCK_ERROR, FAILURE_CODE)

def mock_login_failure(*args, **kwargs):
    return MockResponse(MOCK_ERROR, FAILURE_CODE)

def mock_logout_success(*args, **kwargs):
    return MockResponse(None, SUCCESS_CODE)

def mock_logout_failure(*args, **kwargs):
    return MockResponse(MOCK_ERROR, FAILURE_CODE)


class ImpersonatorTestCase(unittest.TestCase):

    @mock.patch('requests.post', side_effect=mock_post_request)
    @mock.patch('requests.delete', side_effect=mock_logout_success)
    def test_login_execute_logout(self, mock_delete, mock_post):
        client = Impersonator()

        credentials = {
            'username': 'username',
            'password': 'password'
        }
        payload = {
            'token': MOCK_TOKEN,
            'command': MOCK_COMMAND_SUCCESS
        }

        login_endpoint = "http://%s:%d/%s" % (
            client.host,
            client.port,
            client.token_endpoint
        )
        command_endpoint = "http://%s:%d/%s" % (
            client.host,
            client.port,
            client.command_endpoint
        )
        logout_endpoint = "%s/%s" % (
            login_endpoint,
            MOCK_TOKEN
        )

        token = client.login(**credentials)

        self.assertIn(mock.call(login_endpoint, json=credentials), mock_post.call_args_list)
        self.assertEqual(token, MOCK_TOKEN)

        data = client.execute(MOCK_COMMAND_SUCCESS)

        self.assertIn(mock.call(command_endpoint, json=payload), mock_post.call_args_list)
        self.assertEqual(data, MOCK_OUTPUT)

        client.logout()

        self.assertIn(mock.call(logout_endpoint), mock_delete.call_args_list)
        self.assertEqual(client.token, None)


    @mock.patch('requests.post', side_effect=mock_login_failure)
    def test_login_failure(self, mock_post):
        client = Impersonator()

        credentials = {
            'username': 'username',
            'password': 'password'
        }
        endpoint = "http://%s:%d/%s" % (
            client.host,
            client.port,
            client.token_endpoint
        )

        with self.assertRaises(Exception) as context:
            token = client.login(**credentials)

        self.assertIn(mock.call(endpoint, json=credentials), mock_post.call_args_list)
        self.assertEqual(MOCK_ERROR, str(context.exception))


    @mock.patch('requests.post', side_effect=mock_post_request)
    @mock.patch('requests.delete', side_effect=mock_logout_failure)
    def test_logout_failure(self, mock_delete, mock_post):
        client = Impersonator()

        credentials = {
            'username': 'username',
            'password': 'password'
        }
        login_endpoint = "http://%s:%d/%s" % (
            client.host,
            client.port,
            client.token_endpoint
        )
        logout_endpoint = "%s/%s" % (
            login_endpoint,
            MOCK_TOKEN
        )

        token = client.login(**credentials)

        with self.assertRaises(Exception) as context:
            client.logout()

        self.assertIn(mock.call(logout_endpoint), mock_delete.call_args_list)
        self.assertEqual(MOCK_ERROR, str(context.exception))


    @mock.patch('requests.post', side_effect=mock_post_request)
    def test_execute_failure(self, mock_post):
        client = Impersonator()

        credentials = {
            'username': 'username',
            'password': 'password'
        }
        payload = {
            'token': MOCK_TOKEN,
            'command': MOCK_COMMAND_FAILURE
        }

        login_endpoint = "http://%s:%d/%s" % (
            client.host,
            client.port,
            client.token_endpoint
        )
        command_endpoint = "http://%s:%d/%s" % (
            client.host,
            client.port,
            client.command_endpoint
        )

        token = client.login(**credentials)

        with self.assertRaises(Exception) as context:
            client.execute(MOCK_COMMAND_FAILURE)

        self.assertIn(mock.call(command_endpoint, json=payload), mock_post.call_args_list)
        self.assertEqual(MOCK_ERROR, str(context.exception))