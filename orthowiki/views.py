from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Article
from .translations import get_translations


class IndexView(ListView):
    model = Article
    template_name = "orthowiki/index.html"
    context_object_name = "articles_list"
    ordering = ["-mod_date"]

    def get_queryset(self):
        # Get language code from URL kwargs (defaulting to 'en' as a fallback)
        self.lang_code = self.kwargs.get("lang_code", "en")

        # Start with the base queryset (all articles ordered by latest) filtered by language
        queryset = super().get_queryset().filter(language=self.lang_code)
        
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
        lang_code = self.kwargs.get("lang_code", "en")

        # Pass the query and the language to the template so the input box stays populated
        context["query"] = self.request.GET.get("q", "")
        context["current_lang"] = lang_code
        context["t"] = get_translations(lang_code)
        return context


class ArticleView(DetailView):
    model = Article
    template_name = "orthowiki/article.html"
    context_object_name = "article"

    def get_queryset(self):
        # Ensure the article belongs to the language specified in the URL
        lang_code = self.kwargs.get("lang_code", "en")
        return super().get_queryset().filter(language=lang_code)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        lang_code = self.kwargs.get("lang_code", "en")

        # Pass the language to the template
        context["current_lang"] = lang_code
        context["t"] = get_translations(lang_code)
        return context
