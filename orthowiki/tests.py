import hashlib
from datetime import timedelta

from django.test import TestCase
from django.utils import timezone
from django.db import IntegrityError, transaction
from django.urls import reverse

from .models import Article

def create_article(
    title,
    slug,
    language="en",
    content="<p>Article test</p>",
    pub_date=None,
    mod_date=None,
):

    pub_date = pub_date or timezone.now()
    mod_date = mod_date or pub_date

    return Article.objects.create(
        title=title,
        author="Test author",
        slug=slug,
        language=language,
        content=content,
        pub_date=pub_date,
        mod_date=mod_date,
        #Uses slug to avoid duplicate file_hash for different articles with the same content
        file_hash=hashlib.md5(slug.encode('utf-8')).hexdigest()
    )


class ArticleModelTestCase(TestCase):
    def test_save_generates_slug_from_title_when_missing(self):
        '''
        Verify that the model's save method successfully generated the slug from the title
        when the slug is not provided.
        '''
        article = Article.objects.create(
            title="Rotator Cuff Repair",
            author="Test author",
            language="en",
            content="<p>Article test</p>",
            pub_date=timezone.now(),
            mod_date=timezone.now(),
            file_hash="a" * 32
        )

        self.assertEqual(article.slug, "rotator-cuff-repair")
    
    def test_explicit_slug_is_preserved(self):
        '''
        Verify that an explicitly provided slug is preserved.
        '''
        article = create_article("Rotator Cuff", "custom-slug")

        self.assertEqual(article.slug, "custom-slug")

    def test_slug_must_be_unique(self):
        '''
        Verify that creating an article with a duplicate slug raises an IntegrityError.
        '''
        create_article("First Article", "duplicate-slug")
        now = timezone.now()

        with self.assertRaises(IntegrityError), transaction.atomic():
            Article.objects.create(
				title="Second Article",
				author="Test Author",
				slug="duplicate-slug",
				content="Content",
				pub_date=now,
				mod_date=now,
				file_hash="b" * 32,
			)


class IndexViewTests(TestCase):
    def test_index_redirects_to_english(self):
        '''
        Verify that the index view redirects to the English version of the index.
        '''
        response = self.client.get(reverse("orthowiki:root-redirect"))

        self.assertRedirects(
            response,
            reverse("orthowiki:index", kwargs={"lang_code": "en"}),
		)
    
    def test_index_filters_language_orders_and_limits_latest_articles(self):
        '''
        Verify that the index view filters articles by language, orders them by publication date,
        and limits the number of displayed articles.
        '''
        start = timezone.now()
        english_articles = [
			create_article(
				f"English Article {number}",
				f"english-{number}",
				pub_date=start + timedelta(minutes=number),
				mod_date=start + timedelta(minutes=number),
			)
			for number in range(7)
		]
        create_article("Portuguese Article", "portuguese", language="pt")

        response = self.client.get(
			reverse("orthowiki:index", kwargs={"lang_code": "en"})
		)

        shown_slugs = [article.slug for article in response.context["articles_list"]]
        expected_slugs = [article.slug for article in reversed(english_articles[-5:])]
        self.assertEqual(shown_slugs, expected_slugs)
        self.assertEqual(len(shown_slugs), 5)
    
    def test_search_matches_title_and_content_but_stays_in_language(self):
        '''
        Verify that the index view search functionality matches articles based on title and content,
        while filtering by the specified language.
        '''
        title_match = create_article("Shoulder Search Term", "title-match")
        content_match = create_article(
			"Another Article", "content-match", content="<p>Shoulder Search Term</p>"
		)
        create_article(
			"Portuguese Match",
			"portuguese-match",
			language="pt",
			content="<p>Shoulder Search Term</p>",
		)

        response = self.client.get(
			reverse("orthowiki:index", kwargs={"lang_code": "en"}),
			{"q": "shoulder search term"},
		)

        self.assertEqual(
			{article.slug for article in response.context["articles_list"]},
			{title_match.slug, content_match.slug},
		)

class ArticleViewTests(TestCase):
    def test_detail_renders_article_and_modified_date_when_changed(self):
        '''
        Verify that the detail view renders the article content and shows the modified date
        when the article has been modified after publication.
        '''
        published = timezone.now() - timedelta(days=2)
        modified = published + timedelta(days=1)
        article = create_article(
            "Knee Arthroscopy",
            "knee-arthroscopy",
            content="<p>Procedure details</p>",
            pub_date=published,
            mod_date=modified,
        )

        response = self.client.get(
			reverse(
				"orthowiki:article",
				kwargs={"lang_code": "en", "slug": article.slug},
			)
		)

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Knee Arthroscopy")
        self.assertContains(response, "Procedure details")
        self.assertContains(response, "Published on")
        self.assertContains(response, "Modified on")

    def test_detail_omits_modified_date_when_article_is_unchanged(self):
        '''
        Verify that the detail view omits the modified date when the article
        has not been modified after publication.
        '''
        published = timezone.now()
        article = create_article(
			"Unchanged Article",
			"unchanged-article",
			pub_date=published,
			mod_date=published,
		)

        response = self.client.get(
			reverse(
				"orthowiki:article",
				kwargs={"lang_code": "en", "slug": article.slug},
			)
		)

        self.assertContains(response, "Published on")
        self.assertNotContains(response, "Modified on")

    def test_detail_returns_404_for_article_in_another_language(self):
        '''
        Verify that the detail view returns a 404 status code when an article exists in a different language.
        '''
        article = create_article("Artroscopia", "artroscopia", language="pt")

        response = self.client.get(
			reverse(
				"orthowiki:article",
				kwargs={"lang_code": "en", "slug": article.slug},
			)
		)

        self.assertEqual(response.status_code, 404)
