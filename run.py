import os
import sys
import swagman

# collection_file = os.path.join(
#         os.path.dirname(__file__), 'format_number_pm.json'
# )

try:
    collection_file = sys.argv[1]
except IndexError:
    raise Exception('Please provide a filename to continue')

converter = swagman.Converter(collection_file)
swagger_json = converter.convert('json')
print(swagger_json)

# spec = swagman.Spec()
# spec.set_title('abcd')
# spec.set_description('hola'))
# pprint(spec.to_yaml())