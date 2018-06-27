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
from utils import get_env_variable, set_access_token, get_submission_details_json,\
                  get_access_token, check_access_token, get_submission_history, failure_page
# from config.testing_docker import *
import boto3
import json



SESSION_TYPE = 'filesystem'

app = Flask(__name__)

if len(sys.argv) < 2:
    raise('Usage: python app.py [mode]')
if sys.argv[1] == 'prod':
    from config.prod import *
elif sys.argv[1] == 'test_local':
    from config.test_local import *
elif sys.argv[1] == 'test_docker':
    from config.test_docker import *
else:
    raise('Mode not supported.')

app.config.from_object(__name__)

Session(app)
cors = CORS(app, supports_credentials=True)

app.config['SQLALCHEMY_DATABASE_URI'] = SQLALCHEMY_DATABASE_URI
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = SQLALCHEMY_TRACK_MODIFICATIONS

db = SQLAlchemy(app)
db.init_app(app)


sqs = boto3.client('sqs')
resp = sqs.get_queue_url(QueueName='advex')
queue_url = resp['QueueUrl']


def send_job_to_sqs(submission_id, s3_model_key, s3_index_key):
    job = {
        'submission_id': submission_id,
        's3_model_key': s3_model_key,
        's3_index_key': s3_index_key
    }
    message = json.dumps(job)
    resp = sqs.send_message(QueueUrl=queue_url, MessageBody=message)


class User(db.Model):
    """
    access attribute by someuser.user_id
    """
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
        backref=db.backref('submissions', lazy=True), uselist=False)

    def __repr__(self):
        return '<Submission: {}>'.format(self.submission_id)


def resetdb_command():
    db.drop_all()
    db.create_all()


def test():
    Submission.query.delete()
    User.query.delete()

    db.create_all()
    example_user = User(nickname='aircrash', email='dave@example.com', password='hello')
    db.session.add(example_user)
    db.session.commit()
    print(User.query.all())

    example_sub = Submission(user_id=User.query.all()[0].user_id, 
        model_name="VGG-16 v1.0",
        status="submitted",
        s3_model_key="7796f75c-f8f5-4707-901d-edcca3599326", 
        s3_index_key="7796f75c-f8f5-4707-901d-edcca3599326")
    db.session.add(example_sub)
    db.session.commit()
    print(User.query.all())
    print(Submission.query.all())

    example_sub = Submission(user_id=User.query.all()[0].user_id, 
        model_name="VGG-16 v1.0",
        status="submitted",
        s3_model_key="7796f75c-f8f5-4707-901d-edcca3599326", 
        s3_index_key="7796f75c-f8f5-4707-901d-edcca3599326")
    db.session.add(example_sub)
    db.session.commit()
    print(User.query.all())
    print(Submission.query.all())


@app.route("/")
def main():
    if DEBUG:
        resetdb_command()

    test()
    return 'Hello World !'


@app.route("/root")
def root():
    return main()


@app.route('/users', methods=['POST'])
def user_register():
    try:
        form = request.get_json()
        new_user = User(nickname=form['nickname'], 
            email=form['email'], password=form['password'])
        db.session.add(new_user)
        db.session.commit()
        return 'successfully registered!'
    except:
        return failure_page('failed to register')


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page
    
    try:
        user = User.query.get(user_id)
        
        return jsonify({'user_id':user.user_id, 'email':user.email, 'nickname':user.nickname})
    except:
        return failure_page('failed to get user info')


@app.route('/users/<int:user_id>/submissions', methods=['GET'])
def get_user_submissions(user_id):
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    try:
        result = Submission.query.filter_by(user_id=user_id).all()
        result = get_submission_history(result)
        return result
    except:
        return failure_page('failed to get user submissions')


@app.route('/submissions/<int:submission_id>', methods=['GET', 'POST'])
def get_update_submission_detail(submission_id):
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    if request.method == 'GET':
        try:
            submission = Submission.query.get(submission_id)
            return get_submission_details_json(submission)
        except:
            return failure_page('failed to get get submission details')
    else:
        try:
            form = request.get_json()
            submission = Submission.query.get(form['submission_id'])
            submission.feedback = form['feedback']
            db.session.commit()

            return "successfully updated submission details"
        except:
            return failure_page('failed to update submission details')


@app.route('/submit', methods=['POST'])
def make_submission():
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page
        
    try:
        form = request.get_json()
        submission = Submission(user_id=form['user_id'], 
            model_name=form['model_name'],
            status="submitted",
            s3_model_key=form['s3_model_key'], 
            s3_index_key=form['s3_index_key'])
        db.session.add(submission)
        db.session.commit()

        send_job_to_sqs(submission.submission_id, form['s3_model_key'], form['s3_index_key'])
        return "successfully submitted"
    except:
        failure_page("failed to submit, check user id")


@app.route('/login', methods=['POST'])
def login():
    try:
        user = User.query.filter_by(email=request.form['email']).first()
        if user is not None and user.password == request.form['password']:
            token = set_access_token(user.user_id)
            return jsonify({'user_id': user.user_id, 'token': token})
        else:
            return failure_page("user doesn't exists or password doesn't match")
    except:
        return failure_page("failed to login")


@app.route('/logout', methods=['POST'])
def logout():
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    try:
        form = request.get_json()
        del session[str(form['user_id'])]
        return "successfully logout"
    except:
        return failure_page("failed to delete access token")


if __name__ == '__main__':
    app.run(host=HOST, port=PORT)




