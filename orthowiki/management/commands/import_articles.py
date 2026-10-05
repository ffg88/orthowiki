import os, markdown, hashlib, frontmatter
from django.core.management.base import BaseCommand
from django.utils.text import slugify
from django.utils import timezone
from orthowiki.models import Article

class Command(BaseCommand):
    help = 'Imports or updates Markdown articles with YAML frontmatter into Django.'

    def handle(self, *args, **kwargs):
        content_dir = os.path.join('content', 'articles')

        # Check for ".../content/articles/" directory
        if not os.path.exists(content_dir):
            self.stdout.write(self.style.ERROR(f"Directory {content_dir} does not exist."))
            return

        # Track processed slugs to handle deletions later
        processed_slugs = set()

        for filename in os.listdir(content_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(content_dir, filename)

                # Frontmatter loading
                post = frontmatter.load(file_path)
                raw_content = post.content
                metadata = post.metadata
                
                # Get the metadata
                title = metadata.get("title")
                slug = slugify(title)
                language = metadata.get("language", "en")

                # Keep track of this slug as active
                processed_slugs.add(slug)

                # HTML content from markdown
                html_content = markdown.markdown(raw_content)

                # Create hash for version control
                with open(file_path, 'rb') as f:
                    file_bytes = f.read()
                file_hash = hashlib.md5(file_bytes).hexdigest()
                
                # Check if the article already exists in the database by slug
                # As the slug is derived from the title, if the title changes, the article will be considered a new one
                try:
                    article = Article.objects.get(slug=slug)
                    
                    # If the hash matches, the file hasn't changed
                    if article.file_hash == file_hash:
                        self.stdout.write(self.style.NOTICE(f"Skipped (unchanged): {title}"))
                        continue
                        
                    # If it has changed, update it
                    article.title = title
                    article.language = language
                    article.content = html_content
                    article.mod_date = timezone.now()
                    article.file_hash = file_hash
                    article.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Updated: {title}"))

                except Article.DoesNotExist:
                    # If it's a brand new file, create it
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
