from functools import wraps
from json import JSONDecodeError
from uuid import UUID

from cerberus import Validator
from trellio import HTTPService, TCPService, HTTPView, TCPView

from .helpers import json_response


class TrellioValidator(Validator):
    def _validate_type_uuid(self, value):
        try:
            UUID(value, version=4)
        except ValueError:
            return False

        return True


def validate_schema(schema=None, allow_unknown=False):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if schema:
                v = TrellioValidator(schema, allow_unknown=allow_unknown)
                if isinstance(self, HTTPService) or isinstance(self, HTTPView):
                    request = args[0]
                    try:
                        payload = await request.json()
                    except JSONDecodeError:
                        data = await request.text()
                        return json_response({'error': 'invalid json', 'data': data}, status=400)
                    if not v.validate(payload):
                        return json_response({'error': v.errors}, status=400)
                elif isinstance(self, TCPService) or isinstance(self, TCPView):
                    if not v.validate(kwargs):
                        return {'error': v.errors}
            return await func(self, *args, **kwargs)

        return wrapper

    return decorator


def required_params(*params):
    def decorator(func):
        @wraps(func)
        async def wrapper(self, *args, **kwargs):
            if isinstance(self, HTTPService) or isinstance(self, HTTPView):
                request = args[0]
                payload = await request.json()
                missing_params = list(filter(lambda x: x not in payload.keys(), params))
                if missing_params:
                    return json_response({'error': 'required params - {} not found'.format(', '.join(missing_params))})
            elif isinstance(self, TCPService) or isinstance(self, TCPView):
                missing_params = list(filter(lambda x: x not in kwargs.keys(), params))
                if missing_params:
                    return {'error': 'required params - {} not found'.format(', '.join(missing_params))}

            return await func(self, *args, **kwargs)

        return wrapper

    return decorator
