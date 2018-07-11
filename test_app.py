import pytest
from flask import url_for
from flask import json, jsonify
from backend.app import db, User, Submission
import unittest



USER_ID = 1
NICKNAME = 'aircrash'
EMAIL = 'test_dave@example.com'
PASSWORD = 'hello'

User.query.delete()
print(User.query.all())
Submission.query.delete()
print(Submission.query.all())

'''
class TestApp:

    def test_root(self, client):
        res = client.get(url_for('root'))
        expected = jsonify({'success': 'successfully registered!'})
        assert res.status_code == 200
        assert b'Hello World !' in res.data


    def test_post_users(self, client):
        user_data = json.dumps({'nickname':NICKNAME, 'email':EMAIL, 'password':PASSWORD})
        res = client.post('/users',
                          data=user_data,
                          content_type='application/json')
        expected = {'success':'successfully registered!'}
        assert expected == json.loads(res.data)

        res2 = client.post('/users', 
                           data=user_data, 
                           content_type='application/json')
        expected = {'error':'failed to register'}
        assert expected == json.loads(res2.data)


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
        print("NUMBER OF ENTRIES:")
        print(len(users))


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
        print("NUMBER OF ENTRIES:")
        print(len(submissions))
'''

