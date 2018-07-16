[![Build Status](https://travis-ci.com/ShangwuYao/AdvEx_BE.svg?branch=master)](https://travis-ci.com/ShangwuYao/AdvEx_BE)
# AdvEx BackEnd

# Dependencies
python version 3.6
- Flask==1.0.2
- Flask-Session==0.3.1
- Flask-CORS==3.0.6
- Flask-SQLAlchemy==2.3.2
- Sqlalchemy-Utils==0.33.3
- Numpy==1.14.2
- Pytest==3.6.0
- Psycopg2==2.7.5
- boto3==1.7
- pytest-flask==0.10.0

# Docker image
Docker available at [docker hub](https://hub.docker.com/r/awp135/advex/tags/).
For pulling docker:
```bash
docker pull awp135/advex:backend
```

# Usage
Use PostgresSQL, supports two way of testing now (to be refactorized):
## 1. Testing locally: 
First, set configuration settings in environment variables, an example of this is (see examples of configuration in docs/ for detail):
```bash
export SQLALCHEMY_DATABASE_URI="your_postgressql_uri"
export SQLALCHEMY_TRACK_MODIFICATIONS=False
export DEBUG=True
export HOST='0.0.0.0'
export PORT=5000
```
Then, start the backend server by simply:
```bash
./start.sh
```

## 2. Testing with docker:
First, set the environment variables on AWS just as testing locally. 
Then, start the backend server by (the following command maps host port 4000 to docker port 80 and uses 5432 for postgresDB port, see examples of configuration in docs/ for detail):
```bash
docker run -p 4000:80 awp135/advex:backend
```
