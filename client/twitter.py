import json
import oauth2 as oauth
import os
import urllib

import config


class TwitterAPI(object):

    def __init__(self, env_settings):
        self.rest_api = TwitterRestAPI(env_settings)

    def get_resource(self, resource, params):
        """
        Calls the Twitter REST endpoint specified by resource['url'], with REST parameters
        specified in params.
        Also creates a summary object based on values described in resource.

        :param resource: the twitter api resource, eg "followers/list"
        :param params: resource params, eg { "screen_name": "foo", "cursor": "-1"}
        :return: a tuple of summary_data, rest_response_data
        """

        resource_handler = ResourceHandler(resource, params)

        url = resource_handler.get_url()
        results = self.rest_api.get_response(url)

        if not results:
            return None, None

        key_extractor = KeyExtractor(results)
        nested_keys = resource_handler.get_nested_keys_to_extract_from_results()
        for nested_key in nested_keys:
            value = key_extractor.get_nested_value(nested_key)
            if value:
                resource_handler.put_field(nested_key, value)
            else:
                resource_handler.remove_field(nested_key)

        file_path = resource_handler.get_filename()
        TwitterAPI.save_results(results, file_path)

        summary = TwitterAPI.get_summary(resource_handler, results)
        return summary, results

    @staticmethod
    def get_summary(resource_handler, data):

        summary_fields = resource_handler.get_summary_fields()
        num_items, data = resource_handler.get_object_containing_summary_data(data)

        if type(data) is dict:
            summary_result = {field: data[field] for field in summary_fields if field in data}
        else:
            summary_result = {}
        summary_result['num_items'] = num_items

        return {
            'params': resource_handler.get_summary_params(),
            'result': summary_result
        }

    @staticmethod
    def save_results(results, filename):
        full_path = os.path.join(config.PARENT_DATA_FOLDER, filename)
        TwitterAPI.make_path_if_not_exists(full_path)
        with open(full_path, 'w') as f:
            f.write(json.dumps(results, indent=4))

    @staticmethod
    def make_path_if_not_exists(full_path):
        parent_directory = os.path.dirname(full_path)
        if not os.path.exists(parent_directory):
            os.makedirs(parent_directory)


class KeyExtractor(object):

    def __init__(self, response):
        if type(response) is list:
            self.data = response[0]
        else:
            self.data = response

    def get_nested_value(self, nested_key):
        return KeyExtractor._traverse_data_for_value(self.data, nested_key.split("|"))

    @staticmethod
    def _traverse_data_for_value(value, keys):
        if not keys:
            return None
        if type(value) is list:
            results = [KeyExtractor._traverse_data_for_value(v, keys) for v in value]
            results = [r for r in results if r is not None]
            return '|'.join(results)
        if keys[0] not in value:
            return None
        if len(keys) == 1:
            return value[keys[0]]
        return KeyExtractor._traverse_data_for_value(value[keys[0]], keys[1:])


class ResourceHandler(object):

    def __init__(self, resource, params):
        self.resource = resource
        self.params = params

    def get_url(self):
        url_params = {p: self.params[p] for p in self.params if self.params[p]}
        return config.TWITTER_BASE_URL.format(resource=self.resource['url']) + urllib.urlencode(url_params)

    def put_field(self, field, value):
        self.params[field] = value

    def remove_field(self, field):
        self.resource['filename_fields'].remove(field)

    def get_filename(self):
        filename_parts = [self.resource['url']]
        filename_fields = self.resource['filename_fields']

        filename_parts.extend([str(self.params[f]) for f in filename_fields if f in self.params and self.params[f]])
        filename_parts.append("json")
        return '.'.join(filename_parts)

    def get_nested_keys_to_extract_from_results(self):
        if 'summarize_filename_prefix' in self.resource:
            return self.resource['summarize_filename_prefix']
        return []

    def get_summary_fields(self):
        if 'summary_fields' in self.resource:
            return self.resource['summary_fields']
        return []

    def get_summary_params(self):
        return {f: self.params[f] for f in self.resource['filename_fields'] if f in self.params}

    def get_object_containing_summary_data(self, data):
        num_items = None
        if 'data_field' in self.resource and self.resource['data_field']:
            data = data[self.resource['data_field']]
        if type(data) is list and data:
            num_items = len(data)
            data = data[-1]
        return num_items, data


class TwitterRestAPI(object):

    HTTP_STATUS_OKAY = '200'
    HTTP_RATE_LIMIT_EXCEEDED = '429'

    def __init__(self, env_settings):
        consumer_key = env_settings['CONSUMER_KEY']
        consumer_secret = env_settings['CONSUMER_SECRET']
        access_token = env_settings['ACCESS_TOKEN']
        access_secret = env_settings['ACCESS_SECRET']

        consumer = oauth.Consumer(key=consumer_key, secret=consumer_secret)
        token = oauth.Token(key=access_token, secret=access_secret)

        self.client = oauth.Client(consumer, token)

    def get_response(self, url):
        header, response = self.client.request(url, method="GET")

        if header['status'] != TwitterRestAPI.HTTP_STATUS_OKAY:
            print header['status'], response

            if header['status'] == TwitterRestAPI.HTTP_RATE_LIMIT_EXCEEDED:
                exit('Rate limit exceeded')

            return None
        else:
            return json.loads(response)
