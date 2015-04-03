import json
import time
from sys import argv

from client.arguments import ArgumentHandler
from client.config import OAUTH_KEYS
from client.twitter import TwitterAPI
from client.summary import Summarizer

def main(args):
    action, resource, params = ArgumentHandler.parse_command_line_args(args)
    if action in ['get', 'next']:
        get_resource(resource, params)
    elif action == 'summary':
        summarize_items(resource, params)
    return action, resource['rate_limit']

def get_resource(resource, params):
    oauth_keys = ArgumentHandler.get_environment_keys(OAUTH_KEYS)
    summary, data = TwitterAPI(oauth_keys).get_resource(resource=resource, params=params)
    print json.dumps(summary, indent=2)


def summarize_items(resource, params):
    Summarizer.summarize_items(resource=resource, params=params)


#for 'next', keep calling, pacing via the rate_limit
main_args = argv[1:]
while True:
    action, rate_limit = main(main_args)
    if action != 'next':
        exit(0)
    sleep_amount_in_secs = (15 * 60 / rate_limit) + 2 # add 2 seconds for good measure
    print 'sleeping for', sleep_amount_in_secs
    time.sleep(sleep_amount_in_secs)
