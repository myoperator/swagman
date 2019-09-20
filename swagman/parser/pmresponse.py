import json

class pmresponse(object):

    def __init__(self, response):
        self.response = response

    def getMethod(self):
        return self.response['originalRequest'].get('method')

    def getCode(self):
        return self.response['code'] if 'code' in self.response else 200

    def getName(self):
        return self.response['name'] if 'name' in self.response else ''

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
            return 'text/html' if header == 'Content-Type' else None

    def getBody(self):
        responsestr = self.response['body'] if 'body' in self.response \
                        else None
        try:
            return json.loads(responsestr)
        except Exception:
            return responsestr
