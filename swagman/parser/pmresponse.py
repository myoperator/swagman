import json

# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#dataTypeFormat
python2schematypes = {
    int: ('integer', 'int32'),
    list: ('array', None),
    str: ('string', None),
    bool: ('boolean', None),
    dict: ('object', None),
}

class pmresponse(object):

    def __init__(self, response):
        self.response = response

    def getMethod(self):
        return self.response['originalRequest'].get('method')
    
    # def getProperties(self, body):
    #     items = dict()
    #     for key, item in body.items():
    #         if item is not None:
    #             (_type, _format) = python2schematypes[type(item)]
    #             itemdict = {'type': _type}
    #             if _format is not None:
    #                 itemdict['format'] = _format
    #             items[key] = itemdict
    #         else:
    #             items[key] = dict(type = None)
    #     return items

    def getArrayTypes(self, items):
        types = set()
        for item in items:
            (_type, _) = python2schematypes[type(item)]
            types.add(_type)
        return list(types)
    
    def _schemaWalker(self, item):
        if item is None:
            return dict(type = 'string', nullable=True)
        (_type, _format) = python2schematypes[type(item)]
        schema = dict(type = _type)
        if isinstance(item, dict):
            schema['properties'] = dict()
            for k, v in item.items():
                schema['properties'][k] = self._schemaWalker(v)
        elif isinstance(item, int):
            schema['format'] = _format
        elif isinstance(item, bool):
            schema['format'] = _format
        elif isinstance(item, list):
            types = self.getArrayTypes(item)
            schema['items'] = dict()
            if len(types) is 0:
                schema['items'] = {}
            elif len(types) is 1:
                schema['items']['oneOf'] = [self._schemaWalker(v) for v in types]
            else: 
                schema['items'] = self._schemaWalker(types[0])
             
        return schema


    def getSchema(self):
        """Try converting json to see if json is returned in response"""
        body = self.getBody()
        return self._schemaWalker(body)

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
