import pytest
import os
import tempfile
from flask import Flask, session
import flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy_utils import database_exists, create_database, drop_database
from datetime import datetime
from flask import request
from flask import jsonify  
from sqlalchemy.dialects.postgresql import JSON
import numpy as np
import re
import pytest
from AdvEx_BE.utils import *
#from AdvEx_BE.config.testing_local import *

DEBUG = True

SESSION_TYPE = 'filesystem'

#def create_app():
#    app = Flask(__name__)
#
#    app.config.from_object(__name__)
#    Session(app)
#
#    app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
#    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS
#
#    db = SQLAlchemy(app)
#    db.init_app(app)
#
#    return app

@pytest.fixture
def app():
    #app = create_app()
    #app.debug = True
    from AdvEx_BE.app import app
    return app
