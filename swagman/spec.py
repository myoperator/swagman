import random
import re, json
from apispec import APISpec
from .parser.parser import PostmanParser
import jsonpath_rw
#from .ignore import IgnorePlugin
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

    def __init__(self, ignoreschema=None, **options):
        self.spec = APISpec(
            title= self.title,
            version= self.version,
            openapi_version = self.openapi_version,
            plugins=[],
            **options
        )
        self.ignoreschema = ignoreschema
        self._counter = {'example': {}, 'schema': {}}
        self._examples = {}

    def set_title(self, title=None):
        self.spec.title = title or self.title
    
    def set_version(self, version=None):
        self.spec.version = version or self.version
    
    def set_description(self, description=''):
        self.spec.options['info'] = dict(description = (description or self.description))

    def add_component_response(self, name, schema):
        self.spec.components.response(name, schema)
        return self
    
    def add_component_example(self, name, schema):
        if self._counter['example'].get(name, None) is None:
            self._counter['example'] =  {name: 0}
            _name = name
        else:
            self._counter['example'][name] += 1
            _name = name + '_' + str(self._counter['example'][name])
        try:
            self.spec.components.example(_name, schema)
        except DuplicateComponentNameError as e:
            # new schema has same repr?
            self.add_component_example(name, schema)
        return self


    def add_component_schema(self, name, schema):
        if self._counter['schema'].get(name, None) is None:
            self._counter['schema'] =  {name: 0}
            _name = name
        else:
            self._counter['schema'][name] += 1
            _name = name + '_' + str(self._counter['schema'][name])
        try:
            self.spec.components.schema(_name, schema)
        except DuplicateComponentNameError as e:
            # new schema has same repr?
            self.add_component_schema(name, schema)
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
                    schema['example'] = eachparam.get('value')
                requestparams.append({
                    "in": location,
                    "name": eachparam.get('name', ''),
                    "schema": schema
                })
        return requestparams

    def json_get_path(self, match):
        '''return an iterator based upon MATCH.PATH. Each item is a path component,
    start from outer most item.'''
        if match.context is not None:
            for path_element in self.json_get_path(match.context):
                yield path_element
            yield str(match.path)

    def json_update_path(self, json, path, value):
        '''Update JSON dictionnary PATH with VALUE. Return updated JSON'''
        try:
            first = next(path)
            # check if item is an array
            if first.startswith('[') and first.endswith(']'):
                try:
                    first = int(first[1:-1])
                except ValueError:
                    pass
            json[first] = self.json_update_path(json[first], path, value)
            return json
        except StopIteration:
            return value

    def getFilters(self, path, method, code):
        if not len(self.ignoreschema.keys()):
            return []
        for _path, schemas in self.ignoreschema['schema'].items():
            if PostmanParser.camelize(_path) == path:
                for _method, responsecode in schemas.items():
                    if _method == method:
                        return responsecode.get(code, [])
        return []

    def parse_skip(self, expr):
        type_explode = expr.split(':')
        if len(type_explode) > 1 and type_explode[-1] == 'a':
            return ''.join(type_explode[:-1]), True
        return expr, False

    def filterResponse(self, path, method, code, response):
        responsejson = response.getBody()
        filters = self.getFilters(path, method, code)
        if len(filters) > 0:
            for jsonfilter in filters:
                expr, skip  = self.parse_skip(jsonfilter)
                expr = expr if expr else jsonfilter
                jsonpath_expr = jsonpath_rw.parse(expr)
                matches = jsonpath_expr.find(responsejson)
                ignoreprop = PostmanParser.IGNOREPROPKEYVAL if skip else PostmanParser.IGNOREPROP
                for match in matches:
                    responsejson = self.json_update_path(responsejson, self.json_get_path(match), ignoreprop)
        return responsejson

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
            if not item['request'].getBody():
                requestbody = response.getRequestBody()
                requestbodyschema = PostmanParser.schemawalker(requestbody)
                requestbodytype = response.getRequestHeader('Content-Type')

            code = response.getCode()
            reqtype = response.getMethod().lower()
            responseBody = self.filterResponse(camelizeKey, reqtype, code, response)
            responseSchema = PostmanParser.schemawalker(responseBody)
            camelizeKeyExample = PostmanParser.camelize(response.getName())
            ref = self.add_component_schema((camelizeKey + str(code)), responseSchema)
            if requestbody:
                self.set_example(('request' + camelizeKey), camelizeKeyExample, dict(
                    value = requestbody
                ))
            self.set_example(('response' + camelizeKey + str(code)), camelizeKeyExample, dict(
                value = response.getBody()
            ))
            operations[reqtype]['operationId'] = camelizeKey + reqtype
            operations[reqtype]['parameters'] = self.get_params(item['request'])
            if requestbody:
                operations[reqtype]['requestBody'] = dict(
                    content = {
                        requestbodytype: dict(
                            schema = requestbodyschema,
                            examples = self.get_example(('request' + camelizeKey), camelizeKeyExample)
                        )
                    }
                )
            operations[reqtype]['responses'][code] = {
                'description': response.getName(),
                'content': {
                    response.getHeader('Content-Type'): {
                        "schema": self.get_ref('schema', (camelizeKey + str(code))),
                        "examples": self.get_example(('response' + camelizeKey + str(code)), camelizeKeyExample)
                    }
                }
            }

        # Reset schema counter
        self._counter = {'example': {}, 'schema': {}}
        # Return new dict copy from original, containing only filled responses
        # since python3 doesn't allow mutating dict during iteration, that's
        # the best I can do currently. 
        #@TODO fix this please
        newdict = dict()
        for k, v in operations.items():
            if v['responses']:
                newdict[k] = v
        return newdict
    
    def set_example(self, responseKey, exampleKey, exampleBody):
        if responseKey in self._examples:
            self._examples[responseKey][exampleKey] = exampleBody
        else:
            self._examples[responseKey] = {exampleKey: exampleBody}
        self.add_component_example((responseKey + exampleKey),  exampleBody)
        

    def get_example(self, responseKey, exampleKey):
        examples = self._examples[responseKey]
        for exampleKey, example in examples.items():
            ref = self.get_ref('example', (responseKey + exampleKey))
            examples[exampleKey] = ref
        return examples

    def get_ref(self, holder, name):
        refs = self.spec.get_ref(holder, name)
        counter = self._counter[holder].get(name, 0)
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

