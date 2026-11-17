import pytest
from unittest.mock import Mock, MagicMock
from backend.utils.text_client import retry_on_transient_error
from backend.application.services import (
    get_outline_application_service,
    reset_outline_application_service,
    get_content_application_service,
    reset_content_application_service,
)


def test_retry_on_transient_error_succeeds_after_503():
    calls = []

    @retry_on_transient_error(max_retries=3, base_delay=0.01)
    def flaky_func():
        calls.append(len(calls))
        if len(calls) < 2:
            raise Exception("503 Server Error: Service Unavailable")
        return "success"

    result = flaky_func()
    assert result == "success"
    assert len(calls) == 2


def test_retry_on_transient_error_raises_after_max_retries():
    calls = []

    @retry_on_transient_error(max_retries=2, base_delay=0.01)
    def always_failing():
        calls.append(len(calls))
        raise Exception("503 Server Error")

    with pytest.raises(Exception) as excinfo:
        always_failing()
    assert "503 Server Error" in str(excinfo.value)
    assert len(calls) == 2


def test_service_resets():
    s1 = get_outline_application_service()
    reset_outline_application_service()
    s2 = get_outline_application_service()
    assert s1 is not s2

    c1 = get_content_application_service()
    reset_content_application_service()
    c2 = get_content_application_service()
    assert c1 is not c2
