from flask import Flask, session, Blueprint
import flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
import sys
from sqlalchemy_utils import database_exists, create_database, drop_database
from datetime import datetime
from flask import request
from flask import jsonify  
from sqlalchemy.dialects.postgresql import JSON
import numpy as np
import re
import pytest
import boto3
import json
import warnings

from AdvEx_BE.utils import get_env_variable, set_access_token, get_submission_details_json, \
                  get_access_token, check_access_token, get_submission_history, failure_page, \
                  success_page



SESSION_TYPE = 'filesystem'

app = Flask(__name__)

if len(sys.argv) < 2:
    from AdvEx_BE.config.testing_local import *
elif sys.argv[1] == 'production':
    from AdvEx_BE.config.production import *
elif sys.argv[1] == 'testing_local':
    from AdvEx_BE.config.testing_local import *
elif sys.argv[1] == 'testing_docker':
    from AdvEx_BE.config.testing_docker import *
elif 'pytest' in sys.argv[0]:
    from AdvEx_BE.config.testing_local import *
else:
    raise ValueError('Mode not supported.')

app.config.from_object(__name__)

Session(app)
cors = CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)
db.init_app(app)


try:
    sqs = boto3.client('sqs')
    resp = sqs.get_queue_url(QueueName='advex')
    queue_url = resp['QueueUrl']
except:
    # should raise error here
    warnings.warn("sqs not started", UserWarning)


def send_job_to_sqs(submission_id, s3_model_key, s3_index_key):
    job = {
        'submission_id': submission_id,
        's3_model_key': s3_model_key,
        's3_index_key': s3_index_key
    }
    message = json.dumps(job)
    resp = sqs.send_message(QueueUrl=queue_url, MessageBody=message)


class User(db.Model):
    user_id = db.Column(db.Integer, primary_key=True)
    nickname = db.Column(db.String(200), unique=False, nullable=False)
    email = db.Column(db.String(200), unique=True, nullable=False)
    password = db.Column(db.String(200), unique=False, nullable=False)

    def __repr__(self):
        return '<User id: {}, nickname: {}, email: {}>'.format(self.user_id, 
            self.nickname, self.email)


class Submission(db.Model):
    submission_id = db.Column(db.Integer, primary_key=True)
    model_name = db.Column(db.String(80), nullable=False)
    status = db.Column(db.String(80), nullable=False)
    s3_model_key = db.Column(db.String(80), nullable=False)
    s3_index_key = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    feedback = db.Column(JSON, nullable=True)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    
    user = db.relationship('User',
        backref=db.backref('submission', lazy=True), uselist=False)

    def __repr__(self):
        return '<Submission: {}>'.format(self.submission_id)


def resetdb_command():
    db.drop_all()
    db.create_all()


@app.route('/users', methods=['POST'])
def user_register():
    #return failure_page('Registration is disabled.', 403)
    try:
        form = request.get_json()
        new_user = User(nickname=form['nickname'], 
            email=form['email'], password=form['password'])
        db.session.add(new_user)
        db.session.commit()
        return success_page('Successfully registered')
    except Exception as e:
        return failure_page("Failed to register: {0}".format(str(e)), 500)


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page
    
    try:
        user = User.query.get(user_id)
        
        return jsonify({'user_id':user.user_id, 'email':user.email, 'nickname':user.nickname})
    except Exception as e:
        return failure_page("Failed to get user information: {0}".format(str(e)), 500)


@app.route('/users/<int:user_id>/submissions', methods=['GET'])
def get_user_submissions(user_id):
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    try:
        result = Submission.query.filter_by(user_id=user_id).all()
        result = get_submission_history(result)
        return result
    except Exception as e:
        return failure_page("Failed to get submission history: {0}".format(str(e)), 500)


@app.route('/submissions/<int:submission_id>', methods=['GET', 'POST'])
def get_update_submission_detail(submission_id):
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    if request.method == 'GET':
        try:
            submission = Submission.query.get(submission_id)
            return get_submission_details_json(submission)
        except Exception as e:
            return failure_page("Failed to get submission detail: {0}".format(str(e)), 500)
    else:
        try:
            form = request.get_json()
            submission = Submission.query.get(form['submission_id'])
            submission.feedback = form['feedback']
            db.session.commit()

            return success_page("Successfully updated submission detail")
        except Exception as e:
            return failure_page("Failed to update submission detail: {0}".format(str(e)), 500)


@app.route('/submit', methods=['POST'])
def make_submission():
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page
        
    try:
        form = request.get_json()
        submission = Submission(user_id=form['user_id'], 
            model_name=form['model_name'],
            status="Submitted",
            s3_model_key=form['s3_model_key'], 
            s3_index_key=form['s3_index_key'])
        db.session.add(submission)
        db.session.commit()

        send_job_to_sqs(submission.submission_id, form['s3_model_key'], form['s3_index_key'])
        return jsonify({'submission_id': submission.submission_id})
    except Exception as e:
        return failure_page("Failed to submit: {0}".format(str(e)), 500)


@app.route('/login', methods=['POST'])
def login():
    try:
        form = request.get_json()
        user = User.query.filter_by(email=form['email']).first()
        if user is not None and user.password == form['password']:
            token = set_access_token(user.user_id)
            return jsonify({'user_id': user.user_id, 'token': token})
        else:
            return failure_page("Email/Password not matched", 401)
    except Exception as e:
        return failure_page("Failed to log in: {0}".format(str(e)), 500)


@app.route('/logout', methods=['POST'])
def logout():
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    try:
        form = request.get_json()
        del session[str(form['user_id'])]
        return success_page("Successfully logged out")
    except Exception as e:
        return failure_page("Failed to log out: {0}".format(str(e)), 500)


@app.teardown_appcontext
def shutdown_session(exception=None):
    db.session.remove()


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)




