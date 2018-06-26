### for user: put this file in config/ folder ###
# example with testing in docker
import socket

your_password_for_db = 'whatever it is'
SQLALCHEMY_DATABASE_URI = 'postgresql+psycopg2://postgres:{}@{}:5432/postgres'.format(your_password_for_db, socket.gethostbyname('host.docker.internal'))
SQLALCHEMY_TRACK_MODIFICATIONS = False
DEBUG = True
HOST = '0.0.0.0'
PORT = 80
