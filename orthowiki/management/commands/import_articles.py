import markdown, hashlib, frontmatter
from pathlib import Path
from django.conf import settings
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from orthowiki.models import Article

class Command(BaseCommand):
    help = 'Imports or updates Markdown articles with YAML frontmatter into Django.'

    def handle(self, *args, **kwargs):
        content_dir = Path(settings.BASE_DIR) / 'content' / 'articles'

        # Check for "BASE_DIR/content/articles/" directory
        if not content_dir.exists():
            self.stdout.write(self.style.ERROR(f"Directory {content_dir} does not exist."))
            return

        # Track processed slugs to handle deletions later
        processed_slugs = set()

        for file_path in content_dir.rglob('*.md'):
            # Open and read file
            with open(file_path, 'r', encoding='utf-8') as f:
                file_text = f.read()
            
            # Create hash for version control
            file_hash = hashlib.md5(file_text.encode('utf-8')).hexdigest()

            # Frontmatter loading
            post = frontmatter.loads(file_text)
            raw_content = post.content
            metadata = post.metadata
                
            # Get the metadata
            title = metadata.get("title")
            if not title:
                # As the title is used for slug, skips files with no titles
                self.stdout.write(self.style.WARNING(f"Skipping {file_path.name}: Missing 'title' in metadata."))
                continue
            author = metadata.get("author", "John Doe")
            slug = slugify(title)
            language = metadata.get("language", "en")

            # Keep track of this slug as active
            processed_slugs.add(slug)

            # HTML content from markdown
            html_content = markdown.markdown(
                raw_content,
                extensions=["tables"]
            )

            # Check if the article already exists in the database by slug
            # As the slug is derived from the title, if the title changes, the article will be considered a new one
            try:
                article = Article.objects.get(slug=slug)
                    
                # If the hash matches, the file hasn't changed
                if article.file_hash == file_hash:
                    self.stdout.write(self.style.NOTICE(f"Skipped (unchanged): {title}"))
                    continue
                        
                # If it has changed, update the corresponding article
                article.title = title
                article.author = author
                article.language = language
                article.content = html_content
                article.mod_date = timezone.now()
                article.file_hash = file_hash
                article.save()
                    
                self.stdout.write(self.style.SUCCESS(f"Updated: {title}"))

            except Article.DoesNotExist:
                # If it's a new file, create a new article
                current_time = timezone.now() # Get the timestamp once to ensure they are identical

                Article.objects.create(
                    title=title,
                    author=author,
                    slug=slug,
                    language=language,
                    content=html_content,
                    pub_date=current_time,
                    mod_date=current_time,
                    file_hash=file_hash
                )
                self.stdout.write(self.style.SUCCESS(f"Created: {title}"))
                
        # Find and list articles for deletion - whose DB slugs are no longer in the markdown folder
        articles_to_delete = Article.objects.exclude(slug__in=processed_slugs)
        delete_count = articles_to_delete.count()

        if delete_count > 0:
            self.stdout.write(self.style.WARNING(f"\nFound {delete_count} article(s) whose markdown files were removed:"))
            for article in articles_to_delete:
                self.stdout.write(f"  - {article.title} (slug: {article.slug})")

            # Prompt the user for confirmation
            confirm = input("\nDo you want to delete these articles from the database? [y/N]: ").strip().lower()

            if confirm in ['y', 'yes']:
                articles_to_delete.delete()
                self.stdout.write(self.style.SUCCESS(f"Successfully deleted {delete_count} articles."))
            else:
                self.stdout.write(self.style.NOTICE("Deletion aborted. No articles were removed."))