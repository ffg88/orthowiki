from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    title = models.CharField(max_length=200)
    author = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    language = models.CharField(max_length=10, default="en")
    content = models.TextField()
    pub_date = models.DateTimeField(verbose_name="date published")
    mod_date = models.DateTimeField(verbose_name="last modified")
    file_hash = models.CharField(max_length=32)

    def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(self.title)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title


class ContactSubmission(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    submitted_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.name} - {self.subject}"
