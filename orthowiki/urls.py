from django.urls import path
from . import views

app_name = "orthowiki"
urlpatterns = [
    path("", views.root_redirect, name="root-redirect"),
    path("<str:lang_code>/", views.IndexView.as_view(), name="index"),
    path("<str:lang_code>/articles/<slug:slug>/", views.ArticleView.as_view(), name="article"),
    path("<str:lang_code>/about/", views.AboutView.as_view(), name="about"),
    path("<str:lang_code>/contact/", views.ContactView.as_view(), name="contact"),
    path("<str:lang_code>/contact/success/", views.ContactSuccessView.as_view(), name='contact_success')
]
