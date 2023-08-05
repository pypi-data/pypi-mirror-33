import json


class JSONMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if 'application/json' in (request.META.get('CONTENT_TYPE') or ''):
            request.JSON = json.loads(request.body.decode('utf-8'))

        return self.get_response(request)
