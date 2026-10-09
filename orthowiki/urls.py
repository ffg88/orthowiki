from django.urls import path
from django.views.generic import RedirectView
from . import views

app_name = "orthowiki"
urlpatterns = [
    # Redirect /orthowiki/ to /orthowiki/en/ using the named 'index' pattern
    path(
        "", 
        RedirectView.as_view(pattern_name="orthowiki:index", permanent=False), 
        kwargs={"lang_code": "en"}, 
        name="root-redirect"
    ),

    # Language-prefixed routes
    path("<str:lang_code>/", views.IndexView.as_view(), name="index"),
    path("<str:lang_code>/articles/<slug:slug>/", views.ArticleView.as_view(), name="article"),
    path("<str:lang_code>/about/", views.AboutView.as_view(), name="about"),
    path("<str:lang_code>/contact/", views.ContactView.as_view(), name="contact")
]
