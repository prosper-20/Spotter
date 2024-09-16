from django.db import models
from django.utils.text import slugify


class Author(models.Model):
    '''
    Model representing an author
    '''
    full_name = models.CharField(max_length=100)
    date_of_birth = models.DateField(null=True, blank=True, help_text="Author's date of birth")
    bio = models.TextField(max_length=1000, blank=True, null=True)

    def __str__(self):
        return f'{self.full_name}'
    


class Book(models.Model):
    '''
    Model represnting a book
    '''
    title = models.CharField(max_length=200)
    slug = models.SlugField(blank=True, null=True, max_length=100)
    author = models.ManyToManyField(Author)
    publication_date = models.DateField(null=True, blank=True, help_text="Book's publication date")
    isbn = models.CharField(max_length=13, unique=True)
    vote_average = models.FloatField(blank=True, null=True)
    vote_count = models.IntegerField(blank=True, null=True)


    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title
