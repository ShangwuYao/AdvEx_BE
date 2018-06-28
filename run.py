from app import app
from backend.config.testing_local import HOST, PORT

if __name__ == '__main__':
    app.run(host=HOST, port=PORT)