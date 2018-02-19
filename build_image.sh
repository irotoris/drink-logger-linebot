#!/bin/bash
# build and packaging
rm -rf functions/dllbot/package/*
docker run --rm -v $(pwd)/functions/dllbot:/build python:2.7.11 pip install -r /build/requirements.txt -t /build/package
cp functions/dllbot/lambda_function.py functions/dllbot/package/
cd functions/dllbot/package/ && zip -r lambda_function.zip *
