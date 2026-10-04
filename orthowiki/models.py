from django.db import models
from django.utils.text import slugify


class Article(models.Model):
    title = models.CharField(max_length=150, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    content = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True, verbose_name="date published")

    def save(self, *args, **kwargs):
            if not self.slug:
                self.slug = slugify(self.title)
            super().save(*args, **kwargs)

    def __str__(self):
        return self.title
