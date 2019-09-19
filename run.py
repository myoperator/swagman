import os
import swagman

collection_file = os.path.join(
        os.path.dirname(__file__), 'memcache.json'
)

converter = swagman.Converter(collection_file)
swagger_json = converter.convert('yaml')
print(swagger_json)

# spec = swagman.Spec()
# spec.set_title('abcd')
# spec.set_description('hola'))
# pprint(spec.to_yaml())