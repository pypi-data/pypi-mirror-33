#!/usr/local/bin/python3

from escat.api import ElasticsearchCatCli
from escat.config import get_es_client, parse_command_line_args, get_common_cat_api_params


def main(arguments):
    commands = ['aliases', 'allocation', 'count', 'fielddata', 'health', 'indices', 'master', 'nodeattrs', 'nodes',
                'pending_tasks', 'plugins', 'recovery', 'repositories', 'thread_pool', 'shards', 'segments',
                'snapshots', 'templates']

    ns = parse_command_line_args(commands, arguments)

    es = get_es_client(ns.cluster, ns.config)

    es_cli = ElasticsearchCatCli(es)

    command_map = {
        'aliases': es_cli.get_aliases,
        'allocation': es_cli.get_allocation,
        'count': es_cli.get_count,
        'fielddata': es_cli.get_fielddata,
        'health': es_cli.get_health,
        'indices': es_cli.get_indices,
        'master': es_cli.get_master,
        'nodeattrs': es_cli.get_node_attrs,
        'nodes': es_cli.get_nodes,
        'pending_tasks': es_cli.get_pending_tasks,
        'plugins': es_cli.get_plugins,
        'recovery': es_cli.get_recovery,
        'repositories': es_cli.get_repositories,
        'thread_pool': es_cli.get_thread_pool,
        'shards': es_cli.get_shards,
        'segments': es_cli.get_segments,
        'snapshots': es_cli.get_snapshots,
        'templates': es_cli.get_templates
    }

    return command_map[ns.module](get_common_cat_api_params(namespace=ns), ns)

