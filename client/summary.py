import config
import os
from resource import SharedResourceHandler


class Summarizer(object):

    @staticmethod
    def summarize_items(resource, params, summary=True, details=False):

        resource_handler = ResourceHandler(resource, params)

        file_paths = resource_handler.get_filenames()

        if 'desc' in resource and resource['desc']:
            file_paths.reverse()

        lines, endpoints = resource_handler.get_summaries(file_paths)

        file_prefix = resource_handler.file_prefix
        properties = resource_handler.properties

        with open(file_prefix + '.summary-summary.txt', 'w') as f:
            f.write('item\tfilename\t' + '\t'.join(properties) + '\n')
            f.write('\n'.join(endpoints))

        with open(file_prefix + '.summary.txt', 'w') as f:
            f.write('\t'.join(properties) + '\n')
            f.write('\n'.join(lines))

        if summary:
            print 'item\tfilename\t' + '\t'.join(properties) + '\n'
            print '\n'.join(endpoints)

        if details:
            print '\t'.join(properties) + '\n'
            print '\n'.join(lines)

# --------- helper classes for Summarizer ---------


class ResourceHandler(SharedResourceHandler):

    def __init__(self, resource, params):
        super(ResourceHandler, self).__init__(resource, params)
        self.properties = self._get_properties()
        self.file_prefix = self.get_file_prefix()

    def get_file_prefix(self):
        return os.path.join(config.PARENT_DATA_FOLDER,
                            '.'.join(self.filename_parts[:-1]))

    def get_filenames(self):
        file_paths = []
        for (dir_path, dir_names, file_names) in os.walk(config.PARENT_DATA_FOLDER):
            expected_prefix = self.file_prefix
            for f in file_names:
                file_path = os.path.join(dir_path, f)
                if file_path.startswith(expected_prefix) and file_path.endswith('.json') and '.last.' not in file_path:
                    file_paths.append(file_path)
        return file_paths

    def _get_properties(self):
        if 'summarize' in self.resource:
            return self.resource['summarize']
        return None

    def get_summaries(self, file_paths):
        lines = []
        endpoints = []
        for path in file_paths:
            data = self.get_object_from_json_file(path=path, summary=True)

            if self.properties is None:
                excluded_fields = ResourceHandler.get_excluded_fields()
                self.properties = [x for x in data[0].keys() if x not in excluded_fields]

            expected_prefix = self.file_prefix
            file_id = path[(len(expected_prefix)):-5]

            count = str(len(data))
            if type(data) is list:
                endpoints.append('1\t' + file_id + '\t' + self.summarize_item(data[0]))
                endpoints.append(count + '\t' + file_id + '\t' + self.summarize_item(data[-1]))

            for u in data:
                if 'limit' in self.params:
                    self.params['limit'] -= 1
                    if self.params['limit'] < 0:
                        return lines, endpoints
                lines.append(self.summarize_item(u))

        return lines, endpoints

    def summarize_item(self, item):
        x = []
        for p in self.properties:
            keys = p.split("|")
            value = ResourceHandler.find_key(item, keys)
            if not value:
                value = 0
            x.append(ResourceHandler.cleanup_value(value))
        return '\t'.join(x)

    @staticmethod
    def find_key(value, keys):
        if not keys:
            return None
        if type(value) is list:
            results = [ResourceHandler.find_key(v, keys) for v in value]
            results = [r for r in results if r is not None]
            return '|'.join(results)
        if keys[0] not in value:
            return None
        if len(keys) == 1:
            return value[keys[0]]
        return ResourceHandler.find_key(value[keys[0]], keys[1:])

    @staticmethod
    def cleanup_value(item):
        if type(item) is str or type(item) is unicode:
            value = item.encode('utf-8')
            if value:
                value = value.replace('\r\n', '|').replace('\n', '|')
            return value
        else:
            return str(item)

    @staticmethod
    def get_excluded_fields(exclusion_list_filename=None):
        if not exclusion_list_filename:
            exclusion_list_filename = config.EXCLUDED_FIELDS_FILENAME
        path = os.path.join(config.PARENT_DATA_FOLDER, exclusion_list_filename)
        with open(path, 'r') as f:
            return f.read().split("\n")
