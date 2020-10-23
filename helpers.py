import json


def generate_response(status_code, body, headers, is_base_64):
    return {
        'statusCode': status_code,
        'body': body,
        'headers': headers,
    }


def validate_body(body):
    if not body:
        return False

    body_json = json.loads(body)
    size = body_json.get('size')
    from_index = body_json.get('from')
    user_email = body_json.get('user_email')

    return not ((not user_email) or
                (size and (type(size) != int and type(size) != float)) or
                from_index and (type(from_index) != int and type(from_index) != float))


def validate_operator(include, exclude=None):
    if ((include and include['operator'] not in ALLOWED_OPERATORS) or
            (exclude and exclude['operator'] not in ALLOWED_OPERATORS)):
        return {
            'statusCode': 400,
            'body': 'Bad request'
        }


def build_match_query(search_obj, include):
    s = copy.copy(search_obj)
    for match in include:
        # validation_error = validate_operator(match)
        # if validation_error:
        #     return validation_error

        s = s.query('match', **{str(match['name']): str(match['value'])})

    return s
