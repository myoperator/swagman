import os
import json
from .spec import Spec
from .parser import PostmanParser

class Converter(object):
    _ALLOWED_FORMATS_ = ['json', 'yaml']

    def __init__(self, collection_file=None, ignoreschema=None):
        self.collection_json = self.from_collection(collection_file)
        self.ignoreschema = ignoreschema

    def from_collection(self, collection_file=None):
        if not os.path.isfile(collection_file):
            raise FileNotFoundError("Postman collection not found")
        with open(collection_file, 'r') as f:
            return json.load(f)
        return None
    
    def parser(self):
        return PostmanParser(self.collection_json)
    
    def spec(self, baseurl='http://localhost'):
        return Spec(**{'servers': [{'url': baseurl}]}, ignoreschema = self.ignoreschema)

    def convert(self, _format='json'):
        if not _format in self._ALLOWED_FORMATS_:
            raise Exception('Format not allowed. Allowed formats: {}'.format(''.join(self._ALLOWED_FORMATS_)))

        parser = self.parser()
        spec = self.spec()

        # Map required attribs
        spec = self._mapper(spec, parser)

        if _format == 'json':
            return json.dumps(spec.to_dict())
        else:
            return spec.to_yaml()

    def _mapper(self, spec, parser):
        spec.set_title(parser.title)
        spec.set_description(parser.description)
        spec.set_version(parser.version)

        #@TODO make this extend from basemapper
        #items = parser.getItems('http://{{PRIVATE_API_HOST}}/memcache/add') # returns list of paths
        items = parser.getItems()
        for _, item in items.items():
            spec.add_item(item)
        return spec
