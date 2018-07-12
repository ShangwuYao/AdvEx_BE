#!/bin/bash

cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)
cd AdvEx_BE
echo $PYTHONPATH

python app.py testing_local