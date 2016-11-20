# -*- coding:utf-8 -*-
import re
import logging
import json
import requests
import boto3
from boto3.dynamodb.conditions import Attr
from multiprocessing import Process
from collections import Counter, OrderedDict

LINE_REPLY_ENDPOINT = 'https://api.line.me/v2/bot/message/reply'
LINE_CHANNEL_ACCESS_TOKEN = 'YOUR_ATTRIBUTE'
LINE_REQUEST_HEADER = {
    "Content-Type": "application/json",
    "Authorization": "Bearer " + LINE_CHANNEL_ACCESS_TOKEN
}
GOOGLE_API_KEY = 'YOUR_ATTRIBUTE'
GOOGLE_CUSTOM_SEARCH_ID = 'YOUR_ATTRIBUTE'
GOOGLE_CUSTOM_SEARCH_ENDPOINT = 'https://www.googleapis.com/customsearch/v1'
S3_BUCKET_NAME = 'YOUR_ATTRIBUTE'
S3_REGION_DOMAIN = 'YOUR_ATTRIBUTE'
S3_BUCKET_PUBLIC_URL = 'https://' + S3_REGION_DOMAIN + '/' + S3_BUCKET_NAME + '/'
DYNAMODB_TABLE_NAME = 'YOUR_ATTRIBUTE'

logger = logging.getLogger()
logger.setLevel(logging.DEBUG)


def reply_line_messages(reply_token, messages):
    payload = {
        "replyToken": reply_token,
        "messages": messages
    }
    res = requests.post(LINE_REPLY_ENDPOINT,
                        headers=LINE_REQUEST_HEADER, data=json.dumps(payload))
    logger.debug(res)
    logger.debug(res.text)


def put_image_from_google_search_to_s3(drink_name):
    s3 = boto3.resource('s3')
    search_word = drink_name + ' 飲み物'
    payload = {
        "key": GOOGLE_API_KEY,
        "cx": GOOGLE_CUSTOM_SEARCH_ID,
        "alt": "json",
        "num": 1,
        "searchType": "image",
        "safe": "high",
        "q": search_word
    }
    res = requests.get(GOOGLE_CUSTOM_SEARCH_ENDPOINT, params=payload)
    logger.debug(res.text)

    image_url = res.json()['items'][0]['link']
    res = requests.get(image_url)
    if res.status_code == 200:
        with open('/tmp/' + drink_name, 'wb') as file:
            file.write(res.content)
        s3.Object(S3_BUCKET_NAME, drink_name +
                  '.jpg').put(Body=open('/tmp/' + drink_name, 'rb'))


def put_item_drink_log_line_table(post_id, user_id, send_date, drink_name, drink_volume):
    dynamodb = boto3.resource('dynamodb')
    drink_log_line_table = dynamodb.Table(DYNAMODB_TABLE_NAME)

    res = requests.get(S3_BUCKET_PUBLIC_URL + drink_name + '.jpg')
    if res.status_code != 200:
        put_image_from_google_search_to_s3(drink_name)

    res = drink_log_line_table.put_item(
        Item={
            'id': post_id,
            'user_id': user_id,
            'send_date': send_date,
            'drink_name': drink_name,
            'drink_volume': drink_volume
        }
    )
    logger.debug(res)


def convert_drink_log_data_from_msg(msg):
    data = msg.split()
    logger.debug(data)
    if not len(data) == 3:
        logger.warning('Invalid data of drink log message.')
        return []

    try:
        data[2] = int(re.match("\d*", data[2]).group())
    except:
        logger.warning(
            'Invalid data of drink log message, maybe volume data is not number.')
        return []
    logger.debug(data)

    return data


def create_report_data(user_id):
    '''
    @param user_id LINE userId
    @return list of line message format
    '''
    dynamodb = boto3.resource('dynamodb')
    drink_log_line_table = dynamodb.Table(DYNAMODB_TABLE_NAME)
    res_scan_db = drink_log_line_table.scan(
        FilterExpression=Attr('user_id').eq(user_id))
    logger.debug(res_scan_db)
    items = res_scan_db['Items']
    logger.debug(items)
    result = {}
    for item in items:
        if item['drink_name'] in result:
            result = dict(Counter(result) +
                          Counter({item['drink_name']: item['drink_volume']}))
        else:
            result.update({item['drink_name']: item['drink_volume']})

    c = OrderedDict(sorted(result.items(), key=lambda x: x[1], reverse=True))
    logger.debug(c)
    ranking_top_5 = []
    iterater = 0
    for drink_name in c:
        iterater += 1
        logger.debug(drink_name)
        ranking_top_5.append(
            {
                "thumbnailImageUrl": S3_BUCKET_PUBLIC_URL + drink_name + ".jpg",
                "title": drink_name,
                "text": "Total: " + str(c[drink_name]) + "ml",
                "actions": []
            }
        )
        if iterater == 5:
            break

    line_messages = [
        {
            "type": "template",
            "altText": "this is a drink report template",
            "template": {
                "type": "carousel",
                "columns": ranking_top_5
            }
        }
    ]
    logging.debug(line_messages)
    return line_messages


def reply_line_bot(webhook_event_object):
    '''
    Put drink log data from LINE text message event in DynamoDB and reply messages.
    Or reply messages with a drink data report.
    @param webhook_event_object dictionary of LINE webhook event object
    @return True, if webhook_event_object is text message event, otherwise False
    '''
    logger.debug(webhook_event_object)

    if 'replyToken' not in webhook_event_object:
        logger.warning(
            'No reply token in LINE webhook event. Do not reply message.')
        return False
    if 'message' not in webhook_event_object:
        logger.warning('Not message event. Do not reply message.')
        return False
    else:
        if 'text' not in webhook_event_object['message']:
            logger.warning('Not text message event. Do not reply message.')
            return False

    rec_msg = webhook_event_object['message']['text']
    reply_token = webhook_event_object['replyToken']
    if 'userId' in webhook_event_object['source']:
        user_id = webhook_event_object['source']['userId']
    elif 'roomId' in webhook_event_object['source']:
        user_id = webhook_event_object['source']['roomId']
    elif 'groupId' in webhook_event_object['source']:
        user_id = webhook_event_object['source']['groupId']
    logger.debug(user_id)
    if rec_msg.startswith('drink'):
        data = convert_drink_log_data_from_msg(rec_msg)
        if data == []:
            logger.warning('Invalid data of drink log message.')
            msg = [
                  {
                      "type": "text",
                      "text": "Your drink log is invalid format."
                  }
            ]
        else:
            put_item_drink_log_line_table(
                webhook_event_object['message']['id'],
                user_id,
                webhook_event_object['timestamp'],
                data[1],
                data[2]
            )
            msg = [
                  {
                      "type": "text",
                      "text": "OK Log."
                  }
            ]
    elif rec_msg.startswith('report'):
        msg = create_report_data(user_id)

    else:
        msg = [
              {
                  "type": "text",
                  "text": "使い方:\n 1. あなたの飲んだ飲み物を記録します.「drink 飲み物名 飲んだ量(ml)」とLINEしてね.\n 2. いままで飲んだ飲み物を、量が多い順番に5つまで表示します.「report」とLINEしてね."
              }
        ]
    reply_line_messages(reply_token, msg)
    return True


def lambda_handler(event, context):
    jobs = []
    if 'body' in event:
        line_webhook_events_object = json.loads(event['body'])
        for line_webhook_event in line_webhook_events_object['events']:
            job = Process(target=reply_line_bot, args=(line_webhook_event, ))
            job.start()
            jobs.append(job)

        [job.join() for job in jobs]
    else:
        logger.warning('Invalid request data.')
    logger.info('Finished.')
