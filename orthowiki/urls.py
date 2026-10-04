from django.urls import path
from . import views

app_name = "orthowiki"
urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("articles/<slug:slug>/", views.ArticleView.as_view(), name="article")
]
