from argparse import ArgumentParser

from elasticsearch import Elasticsearch
import os
import yaml
import getpass
from escat.utils import get_nested_config_values


def get_config_from_file(cluster_name: str, config_file: str):
    with open(config_file, 'r') as _config_file:
        config: dict = yaml.safe_load(_config_file)['clusters'][cluster_name]
    if 'auth' in config:
        if config['auth']['password']['ask']:
            config['auth']['password'] = getpass.getpass('Enter password: ')
        else:
            config['auth']['password'] = config['auth']['password']['value']
    return config


def get_es_client(cluster_name: str, config_file: str):
    config = get_config_from_file(cluster_name, config_file)
    return Elasticsearch(
        hosts=config['hosts'],
        http_auth=(get_nested_config_values(config.get('auth'), 'username', ''),
                   get_nested_config_values(config.get('auth'), 'password', '')),
        use_ssl=get_nested_config_values(config.get('ssl'), 'enabled', False),
        ca_certs=get_nested_config_values(config.get('ssl'), 'ca_certs', []),
        client_cert=get_nested_config_values(config.get('ssl'), 'cert', ""),
        client_key=get_nested_config_values(config.get('ssl'), 'key', "")
    )


def parse_command_line_args(command_list, args):
    home = os.path.expanduser('~')
    default_config = os.path.join(home, '.escat', 'config.yml')
    argument_parser = ArgumentParser(description='Command line tools for management of Elasticsearch Clusters')
    argument_parser.add_argument('-c', '--cluster', help='The config profile to use', default='default', type=str)
    argument_parser.add_argument('--config', help='Path to config file', default=default_config)
    argument_parser.add_argument('module', choices=command_list)
    argument_parser.add_argument('-v', '--verbose', help='Whether to print output with headers', action='store_true', default=False)
    argument_parser.add_argument('-f', '--format', choices=['json', 'yaml', 'text'], default='text')
    argument_parser.add_argument('-t', '--headers',type=str, help='Comma separated list of headers to return')
    argument_parser.add_argument('-b', '--bytes', choices=['b', 'k', 'kb', 'm', 'mb', 'g', 'gb', 't', 'tb', 'p', 'pb'],
                                 help='Which format to display the bytes metrics in.Only valid for recovery module')
    argument_parser.add_argument('-i', '--indices', help='Comma separated list of indices', type=str)
    argument_parser.add_argument('-a', '--aliases', help='Comma separated list of alises', type=str)
    argument_parser.add_argument('--fields', help='Comma separated list of fields', type=str)
    argument_parser.add_argument('--thread-pool-patterns', help='Comma separated list of regex of required thread pool patterns', type=str)
    argument_parser.add_argument('--repo', '--snapshot-repo', help='Name of the repository of whose the snapshots are queried', type=str)
    argument_parser.add_argument('--template', '--template-name', help='Name of the  template to lookup', type=str)
    return argument_parser.parse_args(args)


def get_common_cat_api_params(namespace):
    params = {}
    verbose = namespace.verbose
    if verbose is not None:
        params['v'] = str(verbose).lower()
    headers = namespace.headers
    if headers is not None:
        params['h'] = headers
    params['format'] = namespace.format
    return params
