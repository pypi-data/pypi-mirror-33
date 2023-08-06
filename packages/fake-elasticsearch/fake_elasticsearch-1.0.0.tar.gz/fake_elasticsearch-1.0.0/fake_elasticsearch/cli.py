# -*- coding: utf8 -*-

from elasticsearch import Elasticsearch
from elasticsearch.client.utils import query_params


class FakeElasticsearch(Elasticsearch):

    @query_params(
        'op_type', 'parent', 'pipeline', 'refresh', 'routing',
        'timeout', 'timestamp', 'ttl', 'version', 'version_type',
        'wait_for_active_shards')
    def index(self, index, doc_type, body, id=None, params=None):
        pass
