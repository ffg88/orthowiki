from django.views.generic import ListView, DetailView
from django.db.models import Q
from .models import Article

# Simple UI text dictionaries
translations = {
    "en": {
        "question_search": "What's on your mind?",
        "search_btn": "Search",
        "clear_search": "Clear search",
        "placeholder_search": "Search articles...",
        "latest_title": "Latest Articles",
        "search_results": "Search results for",
        "no_articles": "No articles are available at the moment.",
        "top_message": "Welcome to OrthoWiki, where people can understand common orthopedic concepts.",
        "bottom_message": "No rights reserved.",
        "menu_about": "About",
        "menu_contact": "Contact",
        "read_more": "Read more →",
        "published_on": "Published on",
        "modified_on": "Modified on",
        "return": "← Return"
    },
    "pt": {
        "question_search": "Qual a sua dúvida?",
        "search_btn": "Buscar",
        "clear_search": "Limpar busca",
        "placeholder_search": "Pesquisar artigos...",
        "latest_title": "Últimos Artigos",
        "search_results": "Resultados da busca por",
        "no_articles": "Nenhum artigo disponível no momento.",
        "top_message": "Bem-vindo a OrthoWiki, onde pessoas podem compreender conceitos comuns em ortopedia.",
        "bottom_message": "Nenhum direito reservado.",
        "menu_about": "Sobre",
        "menu_contact": "Contato",
        "read_more": "Leia mais →",
        "published_on": "Publicado em",
        "modified_on": "Modificado em",
        "return": "← Voltar"
    }
}


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
        context["t"] = translations.get(lang_code, translations["en"])
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
        context["t"] = translations.get(lang_code, translations["en"])
        return context
