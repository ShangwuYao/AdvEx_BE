import pytest
import os
import tempfile

from flaskr import flaskr
from app import create_app


@pytest.fixture
def app():
    app = create_app()
    app.debug = True
    return app
