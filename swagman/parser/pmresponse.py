import json

_postman_previewlanguage = dict(
    json = 'application/json',
    text = 'text/plain',
    html = 'text/html',
    xml = 'application/xml',
)

class pmresponse(object):

    def __init__(self, response):
        self.response = response

    def getMethod(self):
        return self.response['originalRequest'].get('method')

    def getCode(self):
        return self.response['code'] if 'code' in self.response else 200

    def getName(self):
        return self.response['name'] if 'name' in self.response else ''

    def getRequestBody(self):
        if ('originalRequest' in self.response) and \
            'body' in self.response['originalRequest']:
            request = self.response['originalRequest']
            request_content_map = {
                "raw": 'text/plain',
                "urlencoded": 'application/x-www-form-urlencoded',
                "formdata": 'multipart/form-data',
            } 
                # Since we only support modes as described in `request_content_map`
            if request['body']['mode'] in request_content_map.keys():
                bodyitem = request['body'][request['body']['mode']]
                if isinstance(bodyitem, str):
                    return json.loads(bodyitem)
                else:
                    filtereditems = filter(lambda item: ('disabled' not in item) or (item['disabled'] is False), bodyitem)
                    items = dict()
                    for item in filtereditems:
                        items[item['key']] = item['value']
                    return items or None 
            return None
        else:
            return None

    def getRequestHeader(self, header='Content-Type'):
        if ('originalRequest' in self.response) and \
            'header' in self.response['originalRequest']:
            try:
                for response_header in self.response['originalRequest']['header']:
                    if header == response_header['key']:
                        return response_header['value']
                        break

                raise Exception('Header not found')
            except Exception:
                return 'text/html' if header == 'Content-Type' else None
        else:
            raise Exception('Header not found')
        

    def getHeader(self, header=None):
        if header is None:
            raise Exception('Header key is required')
        try:
            for response_header in self.response['header']:
                if header == response_header['key']:
                    return response_header['value']
                    break

            raise Exception('Header not found')
        except Exception:
            # Check for `_postman_previewlanguage` header
            if header == 'Content-Type':
                return _postman_previewlanguage.get(
                    self.response['_postman_previewlanguage'].lower() \
                        if '_postman_previewlanguage' in self.response \
                            else 'text',
                'text/html')
            return None

    def getBody(self):
        responsestr = self.response['body'] if 'body' in self.response \
                        else None
        if responsestr:
            header = self.getHeader('Content-Type')
            if 'text/' in header:
                return responsestr
            try:
                return json.loads(responsestr)
            except Exception:
                return responsestr
        return responsestr
