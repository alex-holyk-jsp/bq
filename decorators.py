import functools
import boto3
import json
from botocore.exceptions import ParamValidationError
from datetime import datetime

from helpers import generate_response


dynamodb = boto3.resource('dynamodb')
table = dynamodb.Table('brightcopy-logs')


def handle_exceptions(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            result = func(*args, **kwargs)
            return result
        except ParamValidationError as ex:
            body = {
                'error': str(ex)
            }
            return generate_response(400, json.dumps(body), args[0].get('headers'), args[0].get('isBase64Encoded'))
        except Exception as ex:
            body = {
                'error': repr(ex)
            }
            return generate_response(500, json.dumps(body), args[0].get('headers'), args[0].get('isBase64Encoded'))
    return wrapper


def log_data(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        result = func(*args, **kwargs)
        try:
            item = {}
            now = datetime.now()
            item['Timestamp'] = int(datetime.timestamp(now))
            body = args[0].get('body')
            body_json = json.loads(body) if body else {}
            item['UserEmail'] = str(body_json.get('user_email'))
            item['Body'] = body or str(None)
            response_body = json.loads(result.get('body'))
            error = response_body.get('error') if response_body else ''
            item['Response'] = json.dumps({
                'statusCode': result.get('statusCode'),
                'error': error
            })
            table.put_item(
                Item=item
            )
        except Exception as ex:
            print(str(ex))
        finally:
            return result
    return wrapper
