import os
from datetime import datetime
from elasticsearch_dsl import Document, Date, Integer, Keyword, Text
from elasticsearch_dsl.connections import connections

# Define a default Elasticsearch client
if os.getenv("OPEN_ES", False):
    connections.create_connection(hosts=[os.getenv("ELASTIC_SEARCH_ENDPOINT", "127.0.0.1")])


class ArticleDocument(Document):
    title = Text(analyzer='snowball', fields={'raw': Keyword()})
    body = Text(analyzer='snowball')
    tags = Keyword()
    published_from = Date()
    lines = Integer()

    class Index:
        name = 'blog'
        settings = {
            'number_of_shards': 2,
        }

    def save(self, **kwargs):
        self.lines = len(self.body.split())
        return super(ArticleDocument, self).save(**kwargs)

    def is_published(self):
        return datetime.now() >= self.published_from


def init_es():
    # create the mappings in elasticsearch
    ArticleDocument.init()
