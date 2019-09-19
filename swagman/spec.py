from apispec import APISpec
from apispec.core import Components
from .parser.parser import PostmanParser

class Spec(object):
    title = 'Swagman'
    version = '1.0.0'
    description = 'A sample description'
    openapi_version = '3.0.0'

    def __init__(self):
        self.spec = APISpec(
            title= self.title,
            version= self.version,
            openapi_version = self.openapi_version,
            info=dict(description= self.description)
        )

    def set_title(self, title=None):
        self.spec.title = title or self.title
    
    def set_version(self, version=None):
        self.spec.version = version or self.version
    
    def set_description(self, description=''):
        self.spec.options = dict(info = dict(description = (description or self.description)))
    
    def set_path(self, path):
        self.spec.path(
            path = path,
            parameters = [
                {
                    'name': 'Content-Type',
                    'in': 'header',
                    'description': 'Content Header'
                }
            ]
        )
        return self

    def add_component_response(self, name, schema):
        self.spec.components.response(name, schema)
        return self
    
    def add_component_schema(self, name, schema):
        self.spec.components.schema(name, schema)
        return self

    def get_operations(self, item):
        operations = dict()
        camelizeKey = PostmanParser.camelize(item['request'].getPath())
        for response in item['responses']:
            code = response.getCode()
            reqtype = response.getMethod().lower()
            ref = self.add_component_schema((camelizeKey + str(code)), response.getSchema())
            operations[reqtype] = dict(
                responses = {
                    f'{code}': {
                        'description': response.getName(),
                        'content': {
                            response.getHeader('Content-Type'): {
                                "schema": self.get_ref('schema', (camelizeKey + str(code)))
                            }
                        }
                    }
                }
            )
        return operations

    def get_ref(self, holder, name):
        return self.spec.get_ref(holder, name)

    def add_item(self, item):
        operations = self.get_operations(item)
        self.spec.path(
            path = item['request'].getPath(),
            operations = operations
        )
        return self

    def to_dict(self):
        return self.spec.to_dict()
    
    def to_yaml(self):
        return self.spec.to_yaml()

