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
        "read_more": "Read more →",
        "published_on": "Published on",
        "modified_on": "Modified on",
        "return": "← Return",
        "next": "Next →",
        "previous": "← Previous",
        "page": "Page",
        "of": "of",
        "about": "About",
        "contact": "Contact"
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
        "read_more": "Leia mais →",
        "published_on": "Publicado em",
        "modified_on": "Modificado em",
        "return": "← Voltar",
        "next": "Próxima →",
        "previous": "← Anterior",
        "page": "Página",
        "of": "de",
        "about": "Sobre",
        "contact": "Contato"
    }
}

def get_translations(lang_code, fallback="en"):
    return translations.get(lang_code, translations[fallback])
