import json
import boto3
from boto3.dynamodb.conditions import Key

from decorators import handle_exceptions


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('brightcopy-logs')


# @handle_exceptions
def logs(event, context):
    body = json.loads(event['body'])
    order = body.get('order')
    user_email = body.get('user_email')
    timestamp = body.get('timestamp')
    desc_order = order == 'desc'

    if user_email:
        key_condition_expression = Key('UserEmail').eq(user_email)

        if timestamp:
            key_condition_expression = key_condition_expression & Key(
                'Timestamp').between(timestamp['from'], timestamp['to'])

        data = table.query(
            KeyConditionExpression=key_condition_expression,
            ScanIndexForward=(not desc_order)
        )
        mapped_data = list(map(mapItem, data['Items']))
    else:
        scan_kwargs = {}
        if timestamp:
            scan_kwargs['FilterExpression'] = Key('Timestamp').between(
                timestamp['from'], timestamp['to'])

        data = table.scan(**scan_kwargs)
        mapped_data = sorted(list(
            map(mapItem, data['Items'])), key=lambda x: x['timestamp'], reverse=desc_order)

    return {
        'statusCode': 200,
        'body': json.dumps(mapped_data)
    }


def mapItem(item):
    return {
        'user_email': item.get('UserEmail'),
        'timestamp': int(item['Timestamp']),
        'body': str(item.get('Body')),
        'response': item.get('Response')
    }
