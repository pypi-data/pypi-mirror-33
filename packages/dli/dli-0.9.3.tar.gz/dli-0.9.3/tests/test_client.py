import unittest
import mock

from dli.client import dli_client


class TestAuth(unittest.TestCase):

    @mock.patch('dli.client.dli_client.requests.post')
    def test_handle_auth_error(self, post):
        text = 'Some server error message'
        post.return_value = mock.Mock(status_code=403, text=text)
        with self.assertRaises(dli_client.AuthenticationFailure) as cm:
            dli_client._get_auth_key('api-key', 'api-root')

        self.assertEqual(str(cm.exception), text)

    @mock.patch('dli.client.dli_client.requests.post')
    def test_unknown_auth_error(self, post):
        """
        Should show a generic response message
        """
        post.return_value = mock.Mock(status_code=403, text='')

        with self.assertRaises(dli_client.AuthenticationFailure) as cm:
            dli_client._get_auth_key('api-key', 'api-root')

        self.assertEqual(
            str(cm.exception),
            dli_client.AuthenticationFailure.GENERIC_ERROR_MESSAGE
        )