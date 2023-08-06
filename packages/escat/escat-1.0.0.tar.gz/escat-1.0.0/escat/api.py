import sys

import elasticsearch


class ElasticsearchCatCli():

    def __init__(self, es: elasticsearch.Elasticsearch):
        self.es = es

    def run_command(self, func, options, **kwargs):
        try:
            return func(params=options, **kwargs)
        except elasticsearch.ElasticsearchException as e:
            print(e)
            sys.exit(1)

    def get_aliases(self, options, namespace=None):
        aliases = namespace.aliases
        a = ','.join(aliases)
        return self.run_command(self.es.cat.aliases, options, name=a)
    
    def get_allocation(self, options, namespace):
        return self.run_command(self.es.cat.allocation, options)
    
    def get_count(self, options, namespace):
        indices = namespace.indices
        if indices is not None:
            return self.run_command(self.es.cat.count, options, index=indices)
        else:
            return self.run_command(self.es.cat.count, options)
    
    def get_fielddata(self, options, namespace):
        fields = namespace.fields
        if fields is not None:
            return self.run_command(self.es.cat.fielddata, options, fields=fields)
        else:
            return self.run_command(self.es.cat.fielddata)
    
    def get_health(self, options, namespace=None):
        return self.run_command(self.es.cat.health, options)
    
    def get_indices(self, options, namespace=None):
        return self.run_command(self.es.cat.indices, options, index=namespace.indices)
    
    def get_recovery(self, options, namespace):
        bytes = namespace.bytes
        if bytes is not None:
            options['bytes'] = bytes
        return self.run_command(self.es.cat.recovery, options)
    
    def get_nodes(self, options, namespace):
        return self.run_command(self.es.cat.nodes, options)
    
    def get_master(self, options, namespace):
        return self.run_command(self.es.cat.master, options)
        
    def get_node_attrs(self, options, namespace):
        return self.run_command(self.es.cat.nodeattrs, options)
    
    def get_pending_tasks(self, options, namespace):
        return self.run_command(self.es.cat.pending_tasks, options)
    
    def get_plugins(self, options, namespace):
        return self.run_command(self.es.cat.plugins, options)
    
    def get_repositories(self, options, namespace):
        return self.run_command(self.es.cat.repositories, options)
    
    def get_thread_pool(self, options, namespace):
        return self.run_command(self.es.cat.thread_pool, options, thread_pool_patterns=namespace.thread_pool_patterns)
    
    def get_shards(self, options, namespace):
        return self.run_command(self.es.cat.shards, options, index=namespace.indices)
    
    def get_segments(self, options, namespace):
        return self.run_command(self.es.cat.segments, options, index=namespace.indices)
    
    def get_snapshots(self, options, namespace):
        repo = namespace.snapshot_repo
        if namespace.snapshot_repo is None:
            raise ValueError('Must define name of repository')
        return self.run_command(self.es.cat.snapshots, options, repository=repo)
    
    def get_templates(self, options, namespace):
        return self.run_command(self.es.cat.templates, options, name=namespace.template)