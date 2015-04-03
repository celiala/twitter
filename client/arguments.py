import os

import config
from resource import SharedResourceHandler


class ArgumentHandler(object):

    @staticmethod
    def parse_command_line_args(args):
        if len(args) < 2 or args[0] not in config.ACTIONS or args[1] not in config.RESOURCE:
            print 'action options:', config.ACTIONS
            print 'resource options:', config.RESOURCE.keys()
            exit(1)

        action = args[0]
        resource = dict(config.RESOURCE[args[1]])

        params = ArgumentHandler.get_params(args[2:])

        resource_handler = ResourceHandler(resource, params)
        if action == 'next':
            params = resource_handler.fill_params_with_last_values()
            action = 'get'

        required_fields = resource_handler.get_required_fields(action)
        missing_fields = [field for field in required_fields if field not in params]

        if missing_fields:
            print "required resource params:", ','.join(missing_fields)
            exit(1)

        return action, resource, params

    @staticmethod
    def get_params(resource_params):
        params = {}
        if resource_params:
            for p in resource_params:
                pair = p.split("=")
                value = pair[1]
                if value == 'None':
                    value = None
                params[pair[0]] = value
        return params

    @staticmethod
    def get_environment_keys(keys):
        result = {}
        error = False
        for k in keys:
            if k in keys and keys[k]:
                result[k] = keys[k]
            elif k in os.environ:
                result[k] = os.environ[k]
            else:
                print 'Please set %s, eg \'export %s="--YOUR-VALUE-HERE--"\'' % (k, k)
                error = True
        if error:
            exit(1)
        return result


class ResourceHandler(SharedResourceHandler):

    def __init__(self, resource, params):
        super(ResourceHandler, self).__init__(resource, params)

    def get_required_fields(self, action):
        if action == 'summary':
            return self.resource['filename_fields'][:-1]
        return self.resource['filename_fields']

    def get_last_filename(self):
        filename = self.resource['url'] + '.last.json'
        return os.path.join(config.PARENT_DATA_FOLDER, filename)

    def fill_params_with_last_values(self):
        last_filename = self.get_last_filename()
        data = self.get_object_from_json_file(path=last_filename, summary=False)

        for param in self.resource['filename_fields']:
            self.params[param] = str(data['params'][param])

        for param, last_value in self.resource['next'].iteritems():
            self.params[param] = str(data['result'][last_value])

        return self.params