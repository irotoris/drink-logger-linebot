#!/bin/bash
# build and packaging
rm -rf functions/dllbot/package/*
docker run --rm -v $(pwd)/functions/dllbot:/build python:2.7.11 pip install -r /build/requirements.txt -t /build/package
cp functions/dllbot/lambda_function.py functions/dllbot/package/
cd functions/dllbot/package/ && zip -r lambda_function.zip *
cd ../../../
aws cloudformation package \
    --template-file template.yaml \
    --s3-bucket $SAM_DST_S3_BUCKET \
    --output-template-file packaged-template.yaml
