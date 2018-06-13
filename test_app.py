import pytest
from flask import url_for



USER_ID = 1
NICKNAME = 'aircrash'
EMAIL = 'dave@example.com'
PASSWORD = 'hello'


class TestApp:

    def test_root(self, client):
        res = client.get(url_for('root'))
        assert res.status_code == 200
        assert b'Hello World !' in res.data


    def test_post_users(self, client):
        user_data = dict(
            nickname=NICKNAME,
            email=EMAIL,
            password=PASSWORD
        )
        res = client.post('/users', data=user_data, follow_redirects=True)
        assert b'successfully registered!' in res.data

        res2 = client.post('/users', data=user_data, follow_redirects=True)
        print(res2.data)
        assert b'failed to register' in res2.data