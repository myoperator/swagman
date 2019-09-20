import random
import re
from apispec import APISpec
from .parser.parser import PostmanParser
from apispec.exceptions import DuplicateComponentNameError

postman_to_openapi_typemap = {
    'text': 'string',
    'string': 'string'
}

class CApiSpec(APISpec):
    def get_schema(self, name):
        return self.components._schemas.get(name, None)

class Spec(object):
    title = 'Swagman'
    version = '1.0.0'
    description = 'A sample description'
    openapi_version = '3.0.0'

    def __init__(self):
        self.spec = CApiSpec(
            title= self.title,
            version= self.version,
            openapi_version = self.openapi_version,
            info=dict(description= self.description)
        )
        self._counter = {}

    def set_title(self, title=None):
        self.spec.title = title or self.title
    
    def set_version(self, version=None):
        self.spec.version = version or self.version
    
    def set_description(self, description=''):
        self.spec.options = dict(info = dict(description = (description or self.description)))

    def add_component_response(self, name, schema):
        self.spec.components.response(name, schema)
        return self
    
    def add_component_schema(self, name, schema):
        self._counter[name] = 0
        try:
            self.spec.components.schema(name, schema)
        except DuplicateComponentNameError as e:
            # new schema has same repr?
            oldschema = self.spec.get_schema(name)
            print((oldschema, schema))
            self._counter[name] += 1
            self.spec.components.schema(name + '_' + str(self._counter[name]), schema)
        return self

    def get_params(self, request):
        requestparams = []
        params = request.getParams()

        for location, param in params.items():                     
            for eachparam in param:
                schema = dict(type='string')
                if eachparam.get('type', None) is not None:
                    schema['type'] = postman_to_openapi_typemap.get(eachparam.get('type'), 'string')
                if eachparam.get('value', None) is not None:
                    schema['default'] = eachparam.get('value')
                requestparams.append({
                    "in": location,
                    "name": eachparam.get('name', ''),
                    "schema": schema
                })
        return requestparams

    def get_operations(self, item):
        operations = dict(
            get = dict(responses = dict()),
            post = dict(responses = dict()),
            put = dict(responses = dict()),
            delete = dict(responses = dict()),
            head = dict(responses = dict()),
        )
        camelizeKey = PostmanParser.camelize(item['request'].getPathNormalised())
        requestbody = item['request'].getBody()
        requestbodyschema = PostmanParser.schemawalker(requestbody)
        requestbodytype = item['request'].getBodyContent()
        for response in item['responses']:
            code = response.getCode()
            reqtype = response.getMethod().lower()
            responseSchema = PostmanParser.schemawalker(response.getBody())
            ref = self.add_component_schema((camelizeKey + str(code)), responseSchema)
            operations[reqtype]['parameters'] = self.get_params(item['request'])
            if requestbody:
                operations[reqtype]['requestBody'] = dict(
                    content = {
                        requestbodytype: dict(
                            schema = requestbodyschema
                        )
                    }
                )
            operations[reqtype]['responses'][code] = {
                'description': response.getName(),
                'content': {
                    response.getHeader('Content-Type'): {
                        "schema": self.get_ref('schema', (camelizeKey + str(code)))
                    }
                }
            }
        
        # Reset schema counter
        self._counter = {}
        # Return new dict copy from original, containing only filled responses
        # since python3 doesn't allow mutating dict during iteration, that's
        # the best I can do currently. 
        #@TODO fix this please
        newdict = dict()
        for k, v in operations.items():
            if v['responses']:
                newdict[k] = v
        return newdict

    def get_ref(self, holder, name):
        refs = self.spec.get_ref(holder, name)
        counter = self._counter.get(name, 0)
        if counter > 0:
            refs = dict(oneOf=[refs])
            for i in range(1, (counter+1)):
                ref = self.spec.get_ref(holder, name + '_' + str(i))
                refs['oneOf'].append(ref)
        return refs

    def add_item(self, item):
        operations = self.get_operations(item)
        self.spec.path(
            path = item['request'].getPathNormalised(),
            operations = operations
        )
        return self

    def to_dict(self):
        return self.spec.to_dict()
    
    def to_yaml(self):
        return self.spec.to_yaml()

