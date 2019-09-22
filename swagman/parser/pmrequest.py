import json
import re

_postman_env_regex = r"\{\{[a-zA-Z0-9_.]+\}\}"
_swagger_env_regex = r"\{[a-zA-Z0-9_.]+\}"
paramlocations = ['header', 'query', 'path']

request_content_map = {
    "raw": 'text/plain',
    "urlencoded": 'application/x-www-form-urlencoded',
    "formdata": 'multipart/form-data',
}
class pmrequest(object):

    paramlocations = {
        'header': 'getHeader',

    }

    def __init__(self, request):
        self.request = request

    def getMethod(self):
        return self.request['method'] if 'method' in self.request else None
    
    def getQuery(self):
        if self.request['url'].get('query', None) is None:
            return None
        return list(map(lambda query: dict(
            name = query.get('key'),
            value = query.get('value'),
        ), self.request['url'].get('query')))

    def getHeader(self, header=None):
        if header is None:
            # Return all headers
            return list(map(lambda header: dict(
                name = header.get('key', None),
                value = header.get('value', None),
                type = header.get('type', 'string'),
            ) ,self.request['header']))
        try:
            for request_header in self.request['header']:
                if header == request_header['key']:
                    return request_header['value']
        except Exception:
            return None
        
    def filterEnvVar(self, item):
        return re.findall(_postman_env_regex, item)

    def cleanVars(self, item):
        if isinstance(item, dict):
            if re.findall(_swagger_env_regex, item['value']):
                item['value'] = None
        elif isinstance(item, str):
            if re.findall(_swagger_env_regex, item):
                item = dict(name = item[1:-1], value = None)
            #item = dict(name = item, value = None)
        return item

    def getParams(self, location=None):
        params = dict()
        for paramlocation in paramlocations:
            paramval = getattr(self, 'get%s' % paramlocation.capitalize())()
            if paramval is not None:
                params[paramlocation] = list(
                    filter(
                        lambda item: isinstance(item, dict) \
                        and ((paramlocation == location) if location is not None else True)
                        and (item['name'] is not '')
                        ,
                        map(
                            self.cleanVars,
                            paramval
                        )
                    )
                )
            if paramlocation == location:
                return params
        return params

    def getPathNormalised(self):
        path = '/'.join(self.getPath())
        return '/'+path if path[0] != '/' else path

    def getPath(self):
        return list(map(lambda path: path[1:-1] if self.filterEnvVar(path) else path, self.request['url']['path']))
    
    def getPathRaw(self):
        return self.request['url']['raw'] if 'url' in self.request else None

    def getBodyContent(self):
        if self.request['body']:
            return request_content_map.get(self.request['body']['mode'], '*/*')
        else: return None

    def getBody(self):
        if 'body' in self.request:
            # Since we only support modes as described in `request_content_map`
            if self.request['body']['mode'] in request_content_map.keys():
                bodyitem = self.request['body'][self.request['body']['mode']]
                if isinstance(bodyitem, str):
                    return bodyitem
                else:
                    filtereditems = filter(lambda item: ('disabled' not in item) or (item['disabled'] is False), bodyitem)
                    items = dict()
                    for item in filtereditems:
                        items[item['key']] = item['value']
                    return items or None 
        return None

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
