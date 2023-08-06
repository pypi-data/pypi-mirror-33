from __future__ import unicode_literals
from django.test import TestCase, override_settings

from django.urls import reverse

def assert_status(response, expected_result=200):
    assert response.status_code == expected_result,\
        'Expected status: {}. Got: {}: {}'.format(
            expected_result,
            response.status_code,
            response.content
        )


class TaskAuthorizationTestCase(TestCase):

    def setUp(self):
        self.url = reverse('task-list')

    @override_settings(TASKENGINE_API_KEY='123')
    def test_requires_api_token(self):
        response = self.client.get(self.url)
        assert_status(response, 403)

    @override_settings(TASKENGINE_API_KEY='123')
    def test_access_granted_with_correct_token(self):
        headers = {
            "Authorization": 'Bearer 123'
        }
        response = self.client.get(self.url, **headers)
        assert_status(response, 200)
