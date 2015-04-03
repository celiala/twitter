import json


class SharedResourceHandler(object):

    def __init__(self, resource, params):
        self.resource = resource
        self.params = params
        self.filename_parts = self.get_filename_parts()

    def get_filename_parts(self):
        filename_parts = [self.resource['url']]
        filename_fields = self.resource['filename_fields']
        filename_parts.extend([str(self.params[f]) for f in filename_fields if f in self.params and self.params[f]])
        return filename_parts

    def get_object_from_json_file(self, path, summary):
        with open(path, 'r') as f:
            if summary and 'summary_data_field' in self.resource and self.resource['summary_data_field']:
                return json.loads(f.read())[self.resource['summary_data_field']]
            else:
                return json.loads(f.read())
