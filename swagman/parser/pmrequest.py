import json


class pmrequest(object):

    def __init__(self, request):
        self.request = request

    def getMethod(self):
        return self.request['method'] if 'method' in self.request else None

    def getHeader(self, header=None):
        if header is None:
            raise Exception('Header key is required')
        try:
            for request_header in self.request['header']:
                if header == request_header['key']:
                    return request_header['value']
        except Exception:
            return None

    def getPath(self):
        path = '/'.join(self.request['url']['path'])
        return '/'+path if path[0] != '/' else path

    def getBody(self):
        returned_body = None
        if 'body' in self.request:
            if 'mode' in self.request['body']:
                mode = self.request['body']['mode']
                if mode in self.request['body']:
                    returned_body = []
                    for param in self.request['body'][mode]:
                        if 'disabled' in param:
                            continue
                        returned_body.append(param)
        return returned_body

    def getUri(self):
        urldict = self.request['url']
        protocol = urldict['protocol'] if 'protocol' in urldict else 'http'
        host = urldict['host'][0] if 'host' in urldict and len(urldict['host']) > 0 else None
        if host:
            host = host + '/' if host[-1] != '/' else host
            path = '/'.join(urldict['path'] if 'path' in urldict else [])
            query_params = []
            if 'query' in urldict:
                for query in urldict['query']:
                    if 'disabled' not in query or (query['disabled'] == False):
                        param = query['key'] + '=' + query['value']
                        query_params.append(param)            
            query_params = ('?' if len(query_params) else '') + '&'.join(query_params)
            url = ('https://' if (protocol == 'https') else 'http://') + host + path + query_params
            return url
        else:
            return None
