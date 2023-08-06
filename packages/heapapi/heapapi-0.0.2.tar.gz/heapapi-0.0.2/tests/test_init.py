import json
import unittest

from mock import patch

from heapapi import HeapAPIClient


class HeapAPIClientTestCase(unittest.TestCase):

    def test_init_missing_app_id(self):
        with self.assertRaises(AssertionError):
            HeapAPIClient(None)

    def test_init_ok(self):
        client = HeapAPIClient(12)
        self.assertEqual(client.app_id, '12')

    @patch('requests.post')
    def test_track(self, request_post):
        client = HeapAPIClient(42)
        resp = client.track('xxx', 'Purchase')

        request_post.assert_called_with(
            'https://heapanalytics.com/api/track',
            data=json.dumps({
                "app_id": "42",
                "identity": "xxx",
                "event": "Purchase"
            }),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp, request_post.return_value)
        resp.raise_for_status.assert_called_with()

    @patch('requests.post')
    def test_track_with_properties(self, request_post):
        client = HeapAPIClient(42)
        resp = client.track('xxx', 'Purchase', {'amount': 12, 'currency': 'USD'})

        request_post.assert_called_with(
            'https://heapanalytics.com/api/track',
            data=json.dumps({
                "app_id": "42",
                "identity": "xxx",
                "event": "Purchase",
                "properties": {"amount": 12, "currency": "USD"}
            }),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp, request_post.return_value)
        resp.raise_for_status.assert_called_with()

    @patch('requests.post')
    def test_add_user_properties(self, request_post):
        client = HeapAPIClient(42)
        resp = client.add_user_properties('xxx', {'age': 22})

        request_post.assert_called_with(
            'https://heapanalytics.com/api/add_user_properties',
            data=json.dumps({
                "app_id": "42",
                "identity": "xxx",
                "properties": {"age": 22}
            }),
            headers={'Content-Type': 'application/json'}
        )
        self.assertEqual(resp, request_post.return_value)
        resp.raise_for_status.assert_called_with()
