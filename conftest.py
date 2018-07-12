import pytest

@pytest.fixture
def app():
    from AdvEx_BE.app import app
    return app


