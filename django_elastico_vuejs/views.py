import os

from django.http import JsonResponse
from django.views.generic import TemplateView
from django_elastico_vuejs.models.api.models import ArticleRequestSerializer, SearchArticleRequestSerializer, \
    Article
from django_elastico_vuejs.models.api.models import ArticleSerializer
from django_elastico_vuejs.models.es.models import init_es, ArticleDocument
from elasticsearch import Elasticsearch
from elasticsearch_dsl import Q
from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import APIView
import logging
import sys
if os.getenv("OPEN_ES", False):
    init_es()
    client = Elasticsearch()

host = os.getenv("LOGSTASH_SERVER_IP",'localhost')
test_logger = logging.getLogger('python-logstash-logger')
test_logger.setLevel(logging.INFO)
# UDP
# test_logger.addHandler(logstash.LogstashHandler(host, 12201, version=1))

# TCP
# test_logger.addHandler(logstash.TCPLogstashHandler(host, 5000, version=1))
#
# test_logger.error('python-logstash: test logstash error message.')
test_logger.info('python-logstash: test logstash info message.')
# test_logger.warning('python-logstash: test logstash warning message.')
#
# # add extra field to logstash message
# extra = {
#     'test_string': 'python version: ' + repr(sys.version_info),
#     'test_boolean': True,
#     'test_dict': {'a': 1, 'b': 'c'},
#     'test_float': 1.23,
#     'test_integer': 123,
#     'test_list': [1, 2, '3'],
# }
# test_logger.info('python-logstash: test extra fields', extra=extra)
# print('done,please see kibana')

class Articles(TemplateView):
    template_name = 'django_elastico_vuejs/articles.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        return context


class AddArticle(APIView):
    def post(self, request):
        print(request.data)
        serializer = ArticleRequestSerializer(data=request.data)
        serializer.is_valid()
        print()
        article_request = serializer.create(serializer.validated_data)

        article_document = ArticleDocument(title=article_request.title,
                                           body=article_request.body,
                                           tags=article_request.tags,
                                           published_from=article_request.published_from)

        article_document.save()
        return Response(data="success", status=status.HTTP_200_OK)


class SearchArticle(APIView):
    def post(self, request):
        serializer = SearchArticleRequestSerializer(data=request.data)
        serializer.is_valid()
        search_request = serializer.create(serializer.validated_data)

        if not search_request.title and not search_request.body and not search_request.tags:
            query = Q('match_all')

        else:
            query = Q('match_none')
            if search_request.title:
                query = Q("fuzzy", title=search_request.title)
            if search_request.body:
                query |= Q("fuzzy", body=search_request.body)
            if search_request.tags:
                query |= Q("terms", tags=search_request.tags)

        return execute_search(query)


class SearchArticleV2(APIView):
    def post(self, request):
        serializer = SearchArticleRequestSerializer(data=request.data)
        serializer.is_valid()
        search_request = serializer.create(serializer.validated_data)

        if not search_request.search_input:
            query = Q('match_all')

        else:
            query = Q('match_none')
            query |= Q("fuzzy", title=search_request.search_input)
            query |= Q("fuzzy", body=search_request.search_input)
            query |= Q("terms", tags=[search_request.search_input])

        return execute_search(query)


def execute_search(query):
    search = ArticleDocument.search().query(query)

    all_results = []

    while True:
        search_results = search.execute().hits
        results = list(
            map(lambda x: Article(x.title, x.body, x.tags, x.published_from, x.is_published, x.lines), search_results))
        if not results:
            break
        all_results += results
        search = search[len(all_results):(len(all_results) + 10)]

    serializer = ArticleSerializer(data=all_results, many=True)
    serializer.is_valid()
    return Response(data=serializer.data, status=status.HTTP_200_OK)


from .tasks import add, mul


class task_demo(APIView):
    def post(self, request):
        res = add.delay(10, 20)
        print(res.task_id)  # 返回task_id
        return JsonResponse({"code": 0, "res": res.task_id})
