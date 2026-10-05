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
            slug = slugify(title)
            language = metadata.get("language", "en")

            # Keep track of this slug as active
            processed_slugs.add(slug)

            # HTML content from markdown
            html_content = markdown.markdown(raw_content)

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
                article.language = language
                article.content = html_content
                article.mod_date = timezone.now()
                article.file_hash = file_hash
                article.save()
                    
                self.stdout.write(self.style.SUCCESS(f"Updated: {title}"))

            except Article.DoesNotExist:
                # If it's a new file, create a new article
                Article.objects.create(
                    title=title,
                    slug=slug,
                    language=language,
                    content=html_content,
                    pub_date=timezone.now(),
                    file_hash=file_hash
                )
                self.stdout.write(self.style.SUCCESS(f"Created: {title}"))
                
        # Find and delete any articles in the DB whose slugs are no longer in the markdown folder
        deleted_count, _ = Article.objects.exclude(slug__in=processed_slugs).delete()
        if deleted_count > 0:
            self.stdout.write(self.style.WARNING(f"Deleted {deleted_count} articles whose markdown files were removed."))
