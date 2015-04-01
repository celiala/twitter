from sys import argv

from client.arguments import ArgumentHandler
from client.config import OAUTH_KEYS
from client.twitter import TwitterAPI


def main():
    action, resource, params = ArgumentHandler.parse_command_line_args(argv[1:])
    if action == 'get':
        get_resource(resource, params)
    elif action == 'summary':
        summarize_items(resource, params)


def get_resource(resource, params):
    oauth_keys = ArgumentHandler.get_environment_keys(OAUTH_KEYS)
    summary, data = TwitterAPI(oauth_keys).get_resource(resource=resource, params=params)
    print summary


def summarize_items(resource, params):
    #dapi.summarize_items(resource=resource, params=params)
    pass


main()
