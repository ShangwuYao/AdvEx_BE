[![Build Status](https://travis-ci.com/ShangwuYao/AdvEx_BE.svg?branch=master)](https://travis-ci.com/ShangwuYao/AdvEx_BE)
# AdvEx BackEnd

# Dependencies
- Flask==1.0.2
- Flask-Session==0.3.1
- Flask-SQLAlchemy==2.3.2
- Sqlalchemy-Utils==0.33.3
- Numpy==1.14.2
- Pytest==3.6.0
- Psycopg2==2.7.5

# Docker image
Docker available at [docker hub](https://hub.docker.com/r/awp135/advex/tags/).
For pulling docker:
```bash
docker pull awp135/advex:backend
```

# Usage
Use PostgresSQL, supports two way of testing now (to be refactorized):
## 1. Testing locally: 
Import the following config file in `app.py`: 
```bash
from config.testing_local import *
```
Then run command:
```bash
python app.py
```

## 2. Testing with docker:
Import the following config file in `app.py` instead:
```bash
from config.testing_docker import *
```
Then run command (mapping host port 4000 to docker port 80, use 5432 for postgresDB port, see examples of configuration files in docs/ for detail):
```bash
docker run -p 4000:80 awp135/advex:backend
```
