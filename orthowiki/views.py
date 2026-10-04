from django.views import generic

from .models import Article


class IndexView(generic.ListView):
    template_name = "orthowiki/index.html"
    context_object_name = "latest_articles_list"

    def get_queryset(self):
        """Return the last five published articles."""
        return Article.objects.order_by("-pub_date")[:5]


class ArticleView(generic.DetailView):
    model = Article
    template_name = "orthowiki/article.html"

