from unittest import mock

MOCK_TIMEZONE = "+1"
os_env_mock = mock.MagicMock(side_effect=lambda value: MOCK_TIMEZONE)
