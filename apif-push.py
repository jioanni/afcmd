import argparse
import requests
import os.path
import json
import yaml
import sys
from functions import payload_builder, get_token, traverser, push_request_executor, yaml_parser

push_parser = argparse.ArgumentParser(description='Push Test to APIF Platform')
push_parser.add_argument('hook', action="store", type=str, help="This is your webhook. It is required. It can be passed as either a URL, or a key from a configuration file.")
push_parser.add_argument('-r', '--recursive', nargs="?", action='append', help='Recursive file-getter')
push_parser.add_argument('-c', '--config', action='store', type=str, help="path to config file")
push_parser.add_argument('-C', '--credentials',
                    help='user credentials. overrides credentials present in config file <username:password>')
push_parser.add_argument('-p', '--path', type=str, nargs="?", action='append', help="this is the path to the files you want to push")
push_parser.add_argument('-k', '--key', action='store', type=str,
                    help='A key from a configuration file. Pulls the related configuration data.')
push_parser.add_argument('-b', '--branch', action='store', type=str, help="The specific branch")

if len(sys.argv) == 1:
    push_parser.print_help(sys.stderr)
    sys.exit(1)

args = push_parser.parse_args()

config_key = None

web_hook = None

auth_token = None

if args.hook.startswith("http" or "https"):
    web_hook = args.hook
else:
    config_key = args.hook

branch = "master"

payload = {
    "resources": []
}

if args.branch:
    branch = args.branch

if args.path:
    if not args.recursive:
        for path in args.path:
            if path[len(path)-1] != os.sep:
                path = path + os.sep
            payload_builder(path, branch, payload)
    else:
        for path in args.path:
            if path[len(path)-1] != os.sep:
                path = path + os.sep


if args.config:
    with open(os.path.join(args.config)) as stream:
        try:
            config_yaml = (yaml.load(stream))
        except yaml.YAMLError as exc:
            print(exc)

if args.recursive:
    for path in args.path:
        traverser(path, branch, payload)


if config_key:
    if not args.config:
        config_yaml = yaml_parser()
    for hook in config_yaml['hooks']:
        key = hook['key']
        if key == config_key:
            web_hook = hook['url']
            if not args.credentials:
                if "credentials" in hook:
                    config_credentials = (hook['credentials']['username'] + ":" + hook['credentials']['password'])
                    args.credentials = config_credentials


if args.credentials:
    auth_token = get_token(args.credentials, web_hook)

push_request_executor(web_hook, auth_token, payload)

