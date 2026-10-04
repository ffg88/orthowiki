from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    pub_date = models.DateTimeField(verbose_name="date published")
    mod_date = models.DateTimeField(verbose_name="last modified", blank=True, null=True)
    file_hash = models.CharField(max_length=32, unique=True, blank=True, null=True)

    def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(self.title)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title
