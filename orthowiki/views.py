from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Article


class IndexView(ListView):
    model = Article
    template_name = "orthowiki/index.html"
    context_object_name = "articles_list"
    ordering = ["-mod_date"]

    def get_queryset(self):
        # Start with the base queryset (all articles ordered by latest)
        queryset = super().get_queryset()
        
        # Get the search query from the URL GET parameters
        self.query = self.request.GET.get("q", "")
        
        if self.query:
            # Filter the queryset if a query exists
            queryset = queryset.filter(
                Q(title__icontains=self.query) | Q(content__icontains=self.query)
            )
        else:
            # If no query, limits to the latest 5 articles
            queryset = queryset[:5]
            
        return queryset
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Pass the query to the template so the input box stays populated
        context["query"] = self.request.GET.get("q", "")
        return context


class ArticleView(DetailView):
    model = Article
    template_name = "orthowiki/article.html"

