### for user: put this file in config/ folder ###
# example with testing locally

your_password_for_db = 'whatever it is'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:{}@{}:5432/postgres'.format(your_password_for_db, '127.0.0.1')
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
HOST = '0.0.0.0'
PORT = 5000

