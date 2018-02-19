# Drink Logger Bot for LINE
LINE BOT to log your drink on AWS Lambda with AWS API Gateway, DynamoDB, S3, Google Custom Search API and LINE Messaging API.
Using AWS SAM.

## Requirements
* `aws-sam-local` :`sam version 0.2.6`
  * Installation: `npm install -g aws-sam-local`
* Python 2.7
* AWS Account
  * API Gateway
  * Lambda
  * DynamoDB
  * S3
* LINE BOT Account
* Google API
  * Custom Search API

## Attribute
Change attributes in `template.yaml`.
* `__AWS_ACCOUNT__`
* `__LINE_CHANNEL_ACCESS_TOKEN__`
* `__GOOGLE_API_KEY__`
* `__GOOGLE_CUSTOM_SEARCH_ID__`
* `__S3_REGION_DOMAIN__`
* `__S3_BUCKET_NAME__`

## Build
1. Set awscli config
1. Set environment variable for `build_image.sh` and a build script of lambda functions.  
```
git clone https://github.com/irotoris/drink_logger_line_bot.git
cd drink_logger_line_bot
export SAM_DST_S3_BUCKET=<YOUR_S3_BUCKET_FOR_AWS_SAM>`
sh build_image.sh
```
1. Generate a template file.
```
sam package \
    --template-file template.yaml \
    --s3-bucket $SAM_DST_S3_BUCKET \
    --output-template-file packaged-template.yaml
```

You get packaged-template.yaml by AWS CloudFormation.

## Deploy
1. Create your LINE BOT Account and Access token
1. Create S3 bucket and Publish
1. Deploy AWS SAM
```
sam deploy \
    --template-file packaged-template.yaml \
    --capabilities CAPABILITY_IAM \
    --stack-name <YOUR_STACK_NAME>
```

You get Bot Endpoint on API Gateway AWS Console, and set LINE BOT ENDPOINT on LINE Developers Console.

## License
MIT License
