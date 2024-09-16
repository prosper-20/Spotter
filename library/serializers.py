from rest_framework import serializers
from .models import Author, Book


class BookSerializer(serializers.ModelSerializer):
    author_names = serializers.SerializerMethodField("get_author_names", read_only=True)
    class Meta:
        model = Book
        fields = ["title", "slug", "author", "author_names", "publication_date", "isbn"]


    def get_author_names(self, obj):
        return [author.full_name for author in obj.author.all()]
    


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = "__all__"