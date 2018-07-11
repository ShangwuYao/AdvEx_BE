#!/bin/bash

cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)
cd backend
echo $PYTHONPATH

python app.py testing_local