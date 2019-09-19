import json
from .pmresponse import pmresponse

# https://github.com/OAI/OpenAPI-Specification/blob/master/versions/3.0.2.md#dataTypeFormat
python2schematypes = {
    int: ('integer', 'int32'),
    list: ('array', None),
    str: ('string', None),
    bool: ('boolean', None),
    dict: ('object', None),
}

class pmschema(object):

    def __init__(self, response):
        self.response = response if isinstance(response, pmresponse) else pmresponse(response)

    def getProperties(self, body):
        items = dict()
        for key, item in body.items():
            if item is not None:
                (_type, _format) = python2schematypes[type(item)]
                itemdict = {'type': _type}
                if _format is not None:
                    itemdict['format'] = _format
                items[key] = itemdict
            else:
                items[key] = dict(type = None)
        return items

    def getSchema(self):
        """Try converting json to see if json is returned in response"""
        body = self.response.getBody()
        (schematype, _) = python2schematypes[type(body)]
        schema = dict(
            type = schematype
        )

        if isinstance(body, dict):
            schema['properties'] = self.getProperties(body)

        return schema