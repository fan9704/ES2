from django.urls import path
from .views import AddArticle, SearchArticle, Articles, SearchArticleV2, task_demo

urlpatterns = [
    path('api/add/', task_demo.as_view()),

    path('api/articles/', AddArticle.as_view(), name="add-articles"),
    path('api/articles/search/', SearchArticle.as_view(), name="search-articles"),
    path('api/articles/searchV2/', SearchArticleV2.as_view(), name="search-articles"),
    path('', Articles.as_view(), name="articles")
]
