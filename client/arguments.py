import os

import config


class ArgumentHandler(object):

    @staticmethod
    def parse_command_line_args(args):
        if len(args) < 2 or args[0] not in config.ACTIONS or args[1] not in config.RESOURCE:
            print 'action options:', config.ACTIONS
            print 'resource options:', config.RESOURCE.keys()
            exit(1)

        action = args[0]
        resource = dict(config.RESOURCE[args[1]])

        resource_params = args[2:]
        params = {}
        if resource_params:
            for p in resource_params:
                pair = p.split("=")
                value = pair[1]
                if value == 'None':
                    value = None
                params[pair[0]] = value

        missing_fields = [field for field in resource['filename_fields']
                          if field not in params
                          and 'summarize_filename_prefix' in resource
                          and field not in resource['summarize_filename_prefix']]

        if missing_fields:
            print "required resource params:", ','.join(missing_fields)
            exit(1)

        return action, resource, params

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
