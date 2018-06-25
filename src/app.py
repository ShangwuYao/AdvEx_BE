from flask import Flask, session
import flask
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS
import os
from sqlalchemy_utils import database_exists, create_database, drop_database
from datetime import datetime
from flask import request
from flask import jsonify  
from sqlalchemy.dialects.postgresql import JSON
import numpy as np
import re
import boto3
import json

app = Flask(__name__)
cors = CORS(app, supports_credentials=True)
DEBUG = True

#os.environ['SESSION_TYPE'] = 'filesystem'
SESSION_TYPE = 'filesystem'
app.config.from_object(__name__)
Session(app)


def get_env_variable(name):
    try:
        return os.environ[name]
    except KeyError:
        message = "Expected environment variable '{}' not set.".format(name)
        raise Exception(message)

# the values of those depend on your setup
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")


DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, 
            pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB)

app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

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
    # TODO: error handling


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
    # TODO: lazy value
    user = db.relationship('User',
        backref=db.backref('submissions', lazy=True), uselist=False)

    def __repr__(self):
        return '<Submission: {}>'.format(self.submission_id)


def resetdb_command():
    db.drop_all()
    db.create_all() # create tables


def set_access_token(user_id):
    user_id = str(user_id) # safe
    rand = np.random.randint(0, (1 << 31) - 1)
    token = "Basic " + user_id + ":" + str(rand)
    session[user_id] = token
    
    return token


def get_access_token(user_id):
    user_id = str(user_id)
    return session[user_id]


def _tokenized(token):
    user_id = re.findall("\ (.*)\:", token)[0]
    return token == get_access_token(user_id)


def check_access_token():
    print(request.headers.get('Authorization'))
    try:
        token = request.headers.get('Authorization')
        if not token:
            return failure_page("invalid access token")
        istokenvalid = _tokenized(request.headers.get('Authorization'))
        if not istokenvalid:
            return failure_page("access token doesn't match")
        return None
    except:
        return failure_page("please log in first")


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


def failure_page(failure_info=""):
    return jsonify({'error': failure_info})


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


def get_submission_detail(submission):
    return jsonify({
                      "submission_id": submission.submission_id,
                      "user_id": submission.user_id,
                      "model_name": submission.model_name,
                      "status": submission.status,
                      "created_at": submission.created_at,
                      "feedback": submission.feedback
                    })


@app.route("/")
def main():
    if DEBUG:
        resetdb_command()

    test()
    return 'Hello World !'

import traceback

@app.route('/users', methods=['POST'])
def user_register():
    form = request.get_json()
    # TODO: valid input
    try:
        # TODO: remove this
        # if DEBUG:
        #     Submission.query.delete()
        #     User.query.delete()

        new_user = User(nickname=form['nickname'], 
            email=form['email'], password=form['password'])
        db.session.add(new_user)
        db.session.commit()
        return 'successfully registered!'
    except Exception as e:
        print('exception')
        traceback.print_exc()
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

    # try:
    result = Submission.query.filter_by(user_id=user_id).all()
    result = get_submission_history(result)
    return result
    # except:
        # return failure_page('failed to get user submissions')


@app.route('/submissions/<int:submission_id>', methods=['GET', 'POST'])
def get_update_submission_detail(submission_id):
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    form = request.get_json()
    if request.method == 'GET':
        try:
            submission = Submission.query.get(submission_id)
            return get_submission_detail(submission)
        except:
            return failure_page('failed to get get submission details')

    else:
        try:
            submission = Submission.query.get(form['submission_id'])
            submission.feedback = request.form['feedback']
            db.session.commit()

            return "successfully updated submission details"
        except:
            return failure_page('failed to update submission details')


@app.route('/submit', methods=['POST'])
def make_submission():
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

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


@app.route('/login', methods=['POST'])
def login():
    form = request.get_json()
    try:
        user = User.query.filter_by(email=form['email']).first()
        if user is not None and user.password == form['password']:
            token = set_access_token(user.user_id)
            return jsonify({'user_id': user.user_id, 'token': token})
        else:
            return failure_page("user doesn't exists or password doesn't match")
    except:
        raise
        return failure_page("failed to login")


@app.route('/logout', methods=['POST'])
def logout():
    returned_page = check_access_token()
    if returned_page is not None:
        return returned_page

    form = request.get_json()
    try:
        del session[str(form['user_id'])]
        return "successfully logout"
    except:
        return failure_page("failed to delete access token")


if __name__ == '__main__':
    app.run()
