import json
import boto3
import copy
from requests_aws4auth import AWS4Auth
from elasticsearch import Elasticsearch, RequestsHttpConnection, helpers
from elasticsearch_dsl import Search, Q
from botocore.exceptions import ParamValidationError

from decorators import log_data, handle_exceptions
from helpers import validate_body, validate_operator, build_match_query


REGION = 'eu-central-1'
SERVICE = 'es'
PORT = 443
HOST = 'search-brightcopy-uxqpgjwoamticncbtxcthj5ejy.eu-central-1.es.amazonaws.com'
ALLOWED_OPERATORS = ('is', 'contains', 'startwith',
                     'exists', 'in', 'more', 'less')


credentials = boto3.Session().get_credentials()
awsauth = AWS4Auth(credentials.access_key, credentials.secret_key,
                   REGION, SERVICE, session_token=credentials.token)


es = Elasticsearch(
    hosts=[{'host': HOST, 'port': PORT}],
    http_auth=awsauth,
    use_ssl=True,
    verify_certs=True,
    connection_class=RequestsHttpConnection
)


@log_data
@handle_exceptions
def esearch(event, context):
    if not validate_body(event['body']):
        raise ParamValidationError(report='Invalid request body')

    body = json.loads(event['body'])
    query = body.get('simple_query')
    include = body.get('include')
    exclude = body.get('exclude')
    size = body['size'] if 'size' in body else 10
    from_index = body['from'] if 'from' in body else 0

    s = Search(using=es, index='api-data')
    if include:
        s = build_match_query(s, include)
    elif query:
        s = s.query('multi_match', query=query)
    else:
        s = s.query('match_all')

    response = s[from_index:size].execute()

    results = []
    for hit in response:
        results.append(hit.to_dict())

    response = {
        'statusCode': 200,
        'body': json.dumps({"items": results})
    }

    return response
