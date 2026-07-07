import os
import sys
from pathlib import Path

import pytest
from starlette.requests import Request

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "Admin_api"))

from app.api.public import _build_image_url


@pytest.mark.parametrize(
    ("env_value", "expected"),
    [
        ("http://202.163.113.251:33336", "http://202.163.113.251:33336/media/restaurants/a.jpg"),
        ("https://example.com", "https://example.com/media/restaurants/a.jpg"),
    ],
)
def test_build_image_url_uses_configured_public_base_url(monkeypatch, env_value, expected):
    monkeypatch.setenv("PUBLIC_BASE_URL", env_value)

    request = Request({"type": "http", "method": "GET", "path": "/public/restaurants", "headers": []})

    assert _build_image_url(request, "media/restaurants/a.jpg") == expected
