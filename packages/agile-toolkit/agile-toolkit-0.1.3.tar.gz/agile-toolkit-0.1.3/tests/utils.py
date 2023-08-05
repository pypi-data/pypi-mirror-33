from unittest import mock


def mock_response(status=200):
    response = mock.Mock()
    response.status_code = status
    return response
