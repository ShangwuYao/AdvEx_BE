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
from utils import *

DEBUG = True

SESSION_TYPE = 'filesystem'
# the values of those depend on your setup
POSTGRES_URL = get_env_variable("POSTGRES_URL")
POSTGRES_USER = get_env_variable("POSTGRES_USER")
POSTGRES_PW = get_env_variable("POSTGRES_PW")
POSTGRES_DB = get_env_variable("POSTGRES_DB")

DB_URL = 'postgresql+psycopg2://{user}:{pw}@{url}/{db}'.format(user=POSTGRES_USER, 
            pw=POSTGRES_PW, url=POSTGRES_URL, db=POSTGRES_DB)


def create_app():
    app = Flask(__name__)

    app.config.from_object(__name__)
    Session(app)

    app.config['SQLALCHEMY_DATABASE_URI'] = DB_URL
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False # silence the deprecation warning

    db = SQLAlchemy(app)
    db.init_app(app)


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
        s3_json_key = db.Column(db.String(80), nullable=False)
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
            s3_json_key="7796f75c-f8f5-4707-901d-edcca3599326")
        db.session.add(example_sub)
        db.session.commit()
        print(User.query.all())
        print(Submission.query.all())

        example_sub = Submission(user_id=User.query.all()[0].user_id, 
            model_name="VGG-16 v1.0",
            status="submitted",
            s3_model_key="7796f75c-f8f5-4707-901d-edcca3599326", 
            s3_json_key="7796f75c-f8f5-4707-901d-edcca3599326")
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


    @app.route("/ping")
    def ping():
        return 'Hi World !'


    @app.route('/users', methods=['POST'])
    def user_register():
        # TODO: valid input
        try:
            # TODO: remove this
            if DEBUG:
                Submission.query.delete()
                User.query.delete()

            new_user = User(nickname=request.form['nickname'], 
                email=request.form['email'], password=request.form['password'])
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
            result = get_submission_ids_json(result)
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
                submission = Submission.query.get(request.form['submission_id'])
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
            
        example_sub = Submission(user_id=request.form['user_id'], 
            model_name=request.form['model_name'],
            status="submitted",
            s3_model_key=request.form['s3_model_key'], 
            s3_json_key=request.form['s3_json_key'])
        db.session.add(example_sub)
        db.session.commit()
        print(User.query.all())
        print(Submission.query.all())
        return "successfully submitted"


    @app.route('/login', methods=['POST'])
    def login():
        try:
            user = User.query.filter_by(email=request.form['email']).first()
            if user.password == request.form['password']:
                token = set_access_token(user.user_id)
                return token
            else:
                return "failed to login"
        except:
            return "user doesn't exists or password doesn't match"


    @app.route('/logout', methods=['POST'])
    def logout():
        returned_page = check_access_token()
        if returned_page is not None:
            return returned_page

        try:
            del session[str(request.form['user_id'])]
            return "successfully logout"
        except:
            return failure_page("failed to delete access token")

    return app


if __name__ == '__main__':
    app = create_app()
    app.run()




