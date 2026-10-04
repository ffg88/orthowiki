import os, datetime, markdown, hashlib
from zoneinfo import ZoneInfo
from django.core.management.base import BaseCommand
from orthowiki.models import Article

class Command(BaseCommand):
    help = 'Imports markdown files to Articles.'

    def handle(self, *args, **kwargs):
        content_dir = os.path.join('content', 'articles')

        if not os.path.exists(content_dir):
            self.stdout.write(self.style.ERROR(f"Directory {content_dir} does not exist."))
            return

        for filename in os.listdir(content_dir):
            if filename.endswith('.md'):
                file_path = os.path.join(content_dir, filename)
                
                slug = os.path.splitext(filename)[0]
                title = slug.replace('-', ' ').title()
                file_stat = os.stat(file_path)
                file_date = datetime.datetime.fromtimestamp(file_stat.st_mtime, tz=ZoneInfo("Europe/Rome"))
                
                with open(file_path, 'r', encoding='utf-8') as file:
                    raw_markdown = file.read()
                
                file_hash = hashlib.md5(raw_markdown.encode('utf-8')).hexdigest()
                
                # Check if the article already exists in the database
                try:
                    article = Article.objects.get(slug=slug)
                    
                    # If the hash matches, the file hasn't changed
                    if article.file_hash == file_hash:
                        self.stdout.write(self.style.NOTICE(f"Skipped (unchanged): {title}"))
                        continue
                        
                    # If it changed, convert markdown and update
                    html_content = markdown.markdown(raw_markdown)
                    article.title = title
                    article.content = html_content
                    article.mod_date = file_date
                    article.file_hash = file_hash
                    article.save()
                    
                    self.stdout.write(self.style.SUCCESS(f"Updated: {title}"))

                except Article.DoesNotExist:
                    # If it's a brand new file, create it
                    pub_date = file_date
                    html_content = markdown.markdown(raw_markdown)
                    
                    Article.objects.create(
                        slug=slug,
                        title=title,
                        content=html_content,
                        pub_date=pub_date,
                        file_hash=file_hash
                    )
                    self.stdout.write(self.style.SUCCESS(f"Created: {title}"))
