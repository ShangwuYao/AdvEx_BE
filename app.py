from flask import Flask
from flask_sqlalchemy import SQLAlchemy
import os
from sqlalchemy_utils import database_exists, create_database, drop_database
from datetime import datetime
from flask import request
from flask import jsonify  
from sqlalchemy.sql import select

app = Flask(__name__)
DEBUG = True



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
    s3_model_key = db.Column(db.String(80), nullable=False)
    s3_json_key = db.Column(db.String(80), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    user_id = db.Column(db.Integer, db.ForeignKey('user.user_id'), nullable=False)
    # TODO: lazy value
    user = db.relationship('User',
        backref=db.backref('submissions', lazy=True), uselist=False)

    def __repr__(self):
        return '<Submission: {}>'.format(self.submission_id)


@app.cli.command('resetdb')
def resetdb_command():
    """Destroys and creates the database + tables."""
    if database_exists(DB_URL):
        print('Deleting database.')
        drop_database(DB_URL)
    if not database_exists(DB_URL):
        print('Creating database.')
        create_database(DB_URL)

    print('Creating tables.')
    db.create_all()
    print('Shiny!')


def test():
    User.query.delete()

    db.create_all()
    example_user = User(nickname='aircrash', email='dave@example.com', password='hello')
    db.session.add(example_user)
    db.session.commit()
    print(User.query.all())

    example_sub = Submission(user_id=User.query.all()[0].user_id, 
        s3_model_key="7796f75c-f8f5-4707-901d-edcca3599326", 
        s3_json_key="7796f75c-f8f5-4707-901d-edcca3599326")
    db.session.add(example_sub)
    db.session.commit()
    print(User.query.all())
    print(Submission.query.all())


def get_submission_ids_json(submissions):
    return jsonify({'submission_ids': [submission.submission_id for submission in submissions]})


def failure_page(failure_info=""):
    return failure_info


@app.route("/")
def main():
	#test()
	return 'Hello World !'


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
        new_user = User(nickname='aircrash', email='dave@example.com', password='hello')
        db.session.add(new_user)
        db.session.commit()
        return 'successfully registered!'
    except:
        return failure_page('failed to register')


@app.route('/users/<int:user_id>', methods=['GET'])
def get_user_info(user_id):
    try:
        user = User.query.get(user_id)
        
        return jsonify({'user_id':user.user_id, 'email':user.email, 'nickname':user.nickname})
    except:
        return failure_page('failed to get user info')


@app.route('/users/<int:user_id>/submissions', methods=['GET'])
def get_user_submissions(user_id):
    try:
        result = Submission.query.filter_by(user_id=user_id).all()
        result = get_submission_ids_json(result)
        return result
    except:
        return failure_page('failed to get user submissions')


if __name__ == '__main__':
	app.run()



