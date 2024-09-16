from django.urls import path
from .views import BookAPIView, SingleBookAPIView, AuthorAPIView, SingleAuthorAPIView,AddToFvouriteAPIView, RemoveFavouriteBookView, SuggestedBooksView, RecommenderAPIView

urlpatterns = [
    path("books/", BookAPIView.as_view(), name="list-all-books"),
    path("books/<int:id>/", SingleBookAPIView.as_view(), name="retrieve-single-book"),
    path("books/<int:id>/recommend/", RecommenderAPIView.as_view(), name="recommend-books"),
    path("books/<int:id>/add/", AddToFvouriteAPIView.as_view(), name="add-to-fave"),
    path("books/<int:id>/remove/", RemoveFavouriteBookView.as_view(), name="remove-from-fave"),
    path("authors/", AuthorAPIView.as_view(), name="list-all-authors"),
    path('suggested-books/', SuggestedBooksView.as_view(), name='suggested_books'),
    path("authors/<int:id>/", SingleAuthorAPIView.as_view(), name="retrieve-single-author"),
]