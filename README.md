[![Build Status](https://travis-ci.com/ShangwuYao/AdvEx_BE.svg?branch=master)](https://travis-ci.com/ShangwuYao/AdvEx_BE)
# AdvEx BackEnd
### About AdvEx
AdvEx is a web service for assessing the robustness of machine learning models with adversarial machine learning. It is designed to satisfy the following quality attributes:
- **Scalability**: achieved by auto-scaling and load-balancing using elastic beanstalk
- **Availability**: achieved by having different servers in different availability zones
- **Performance**: achieved by using GPU in evaluation workers, and having users upload their models directly to S3 buckets without going through servers first
- **Security**: achieved by using AWS security group
- **Usability**: achieved by creating helpful instructions and tutorials for users who are not machine learning experts
- **Configurability**: achieved by using Elastic Beanstalk, Docker and config files

Links:

[Project video demo](https://www.youtube.com/watch?v=KJ1zZsia5yQ) | [Front-end static demo](https://dnc1994.com/AdvEx-FE/) | [Front-end repo](https://github.com/dnc1994/AdvEx-FE) | [Back-end repo](https://github.com/ShangwuYao/AdvEx_BE) | [Evaluation worker repo](https://github.com/ShangwuYao/AdvEx_Evaluation)

### Cloud-based system architecture 

<p align="center">
<img src="https://pic-markdown.s3.amazonaws.com/region=us-west-2&tab=overview/2018-08-06-013104.png" width=600 height=500/>
</p>

### Tech Stack
<p align="center">
<img src="https://pic-markdown.s3.amazonaws.com/region=us-west-2&tab=overview/2018-08-06-021058.png" width=600 height=300/>
</p>

### Backend Features
- Supports RESTful APIs for user and submission data, implemented with Flask and PostgreSQL
- Adopts an automatic build, test and deploy workflow using Docker, pytest and Travis-CI, improves code quality with continuous integration
- Handles auto-scaling and load-balancing with Elastic Beanstalk and Docker, reduces deployment time of a new version to 5 min

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
Supports two ways of deploying:
## 1. Testing locally: 
First, set configuration settings in environment variables, an example of this is (see [examples of configuration](https://github.com/ShangwuYao/AdvEx_BE/tree/master/docs) in docs/ for detail):
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

## 2. Deploying on AWS using docker:
First, set the environment variables on AWS just as testing locally. 
Then, start the backend server by (the following command maps host port 4000 to docker port 80 and uses 5432 for postgresDB port, see examples of configuration in docs/ for detail):
```bash
docker run -p 4000:80 awp135/advex:backend
```
