#!/bin/bash

cd ..
export PYTHONPATH=$PYTHONPATH:$(pwd)
ls
cd AdvEx_BE

python app.py