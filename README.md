# Drink Logger Bot for LINE
This program is LINE BOT to log your drink on AWS Lambda with AWS API Gateway, DynamoDB, S3, Google Custom Search API and LINE Messaging API.

## Requirements
* Python 2.7
* Your AWS Account
  * API Gateway
  * Lambda
  * DynamoDB
  * S3
* Your LINE BOT Account
* Google API
  * Custom Search API

## Attribute
You need to change attributes in `drink_logger_line_bot.py`.
* `LINE_CHANNEL_ACCESS_TOKEN`
* `GOOGLE_API_KEY`
* `GOOGLE_CUSTOM_SEARCH_ID`
* `S3_REGION_DOMAIN`
* `S3_BUCKET_NAME`

## Deploy
1. Create your LINE BOT Account and Access token
1. Create S3 bucket and Publish
1. Create DyanmoDB table
  * primary key `id`
1. Deploy codes to Lambda and Configure API Gateway
  * `git clone https://github.com/irotoris/drink_logger_line_bot.git`
  * `cd drink_logger_line_bot && pip install -r requirements.txt -t ./`
  * Configure attributes in `drink_logger_line_bot.py`
  * `zip -r upload.zip ./*`
  * Upload `upload.zip` to AWS Lambda
  * Configure Lambda Trigger (->API Gateway)
1. Configure LINE BOT Webhook URL (->API Gateway URL)

## License
MIT License
