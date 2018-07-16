import pytest
from flask import url_for
from flask import json, jsonify
from AdvEx_BE.app import db, User, Submission
import unittest



USER_ID = 1
NICKNAME = 'aircrash'
EMAIL = 'test_dave@example.com'
PASSWORD = 'hello'

# clean up test database
db.drop_all()
db.create_all()
db.session.commit()

class TestApp:

    def test_register_users(self, client):
        user_data = json.dumps({'nickname':NICKNAME, 'email':EMAIL, 'password':PASSWORD})
        res = client.post('/users',
                          data=user_data,
                          content_type='application/json')
        expected = {'success':'Successfully registered'}
        assert expected == json.loads(res.data)

        res2 = client.post('/users', 
                           data=user_data, 
                           content_type='application/json')
        expected = {'error':'Failed to register'}
        assert 'Failed to register' in json.loads(res2.data)['error']


class TestUser(unittest.TestCase):

    def test_lookup(self):

        user = User(
            nickname='Dave',
            email='dave@gmail.com',
            password='aircrash'
        )

        db.session.add(user)
        db.session.commit()

        users = User.query.all()

        assert user in users


class TestSubmission(unittest.TestCase):

    def test_lookup(self):

        submission = Submission(
            user_id=1,
            model_name='VGG-16 v1.0',
            status='submitted',
            s3_model_key='model.h5',
            s3_index_key='index.json'
        )

        db.session.add(submission)
        db.session.commit()

        submissions = Submission.query.all()

        assert submission in submissions


