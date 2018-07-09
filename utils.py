from flask import Flask, session
import flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy_utils import database_exists, create_database, drop_database
from datetime import datetime
from flask import request
from flask import jsonify
from flask import make_response
from sqlalchemy.dialects.postgresql import JSON
import numpy as np
import re
import pytest



def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)


def set_access_token(user_id):
    user_id = str(user_id) # safe
    rand = np.random.randint(0, (1 << 31) - 1)
    token = "Basic " + user_id + ":" + str(rand)
    session[user_id] = token
    
    return token


def get_access_token(user_id):
    user_id = str(user_id)
    try:
      return session[user_id]
    except:
      return None


def _tokenized(token):
    user_id = re.findall("\ (.*)\:", token)[0]
    real_token = get_access_token(user_id)
    return real_token is not None and real_token == token


def check_access_token():
    try:
        istokenvalid = _tokenized(request.headers.get('Authorization'))
        if not istokenvalid:
            return failure_page("Invalid access token", 401)
        return None
    except Exception as e:
        return failure_page("Failed to check access token: {0}".format(str(e)), 500)


def failure_page(failure_info="", status=200):
    response = jsonify({'error': failure_info})
    return make_response((response, status))


def success_page(display_info=""):
    return jsonify({'success': display_info})
    

def get_submission_history(submissions):
    return jsonify({'submissions': [get_submission_detail_without_feedback(submission) for submission in submissions]})


def get_submission_detail_without_feedback(submission):
    return {
      "submission_id": submission.submission_id,
      "user_id": submission.user_id,
      "model_name": submission.model_name,
      "status": submission.status,
      "created_at": submission.created_at
    }


def get_submission_details_json(submission):
    return jsonify({
                      "submission_id": submission.submission_id,
                      "user_id": submission.user_id,
                      "model_name": submission.model_name,
                      "status": submission.status,
                      "created_at": submission.created_at,
                      "feedback": submission.feedback
                    })



