from app import app
from AdvEx_BE.utils import get_env_variable

HOST = get_env_variable('HOST')
PORT = get_env_variable('PORT')


if __name__ == '__main__':	
    app.run(host=HOST, port=PORT)