import unittest
import random

from backend.app import app, db, User, Submission
from backend.config.testing import *
    
db.session.commit()
db.drop_all()
db.create_all()
'''
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
            s3_json_key='index.json'
        )

        db.session.add(submission)
        db.session.commit()

        submissions = Submission.query.all()

        assert submission in submissions
        print("NUMBER OF ENTRIES:")
        print(len(submissions))
'''

#class TestMain(unittest.TestCase):
def test_empty_db(client):

    rv = client.get('/')
    print("res", rv.data)
    assert b'Hello World !' in rv.data


