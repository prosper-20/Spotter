from django.shortcuts import render, get_object_or_404
from .serializers import BookSerializer, AuthorSerializer
from rest_framework.views import APIView
from .models import Book, Author
from rest_framework.response import Response
from rest_framework import status
from django.http import Http404
from django.db.models import Q
from rest_framework.filters import SearchFilter
from rest_framework.generics import ListCreateAPIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from accounts.models import Profile
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import linear_kernel
import numpy as np
from django.db.models import Avg



class BookAPIView(ListCreateAPIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow anyone to view authors
            return [AllowAny()]
        elif self.request.method == 'POST':
            # Only authenticated users can create (POST) authors
            return [IsAuthenticated()]
        return super().get_permissions()
    

    serializer_class = BookSerializer
    queryset = Book.objects.all()
    filter_backends = [SearchFilter]
    search_fields = ["title", "author__full_name"]

    


class SingleBookAPIView(APIView):
    def get_object(self, id):
        try:
            return Book.objects.get(id=id)
        except Book.DoesNotExist:
            raise Http404


    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow anyone to view books
            return [AllowAny()]
        elif self.request.method == 'PUT':
            # Only authenticated users can update (PUT) books
            return [IsAuthenticated()]
        elif self.request.method == 'DELETE':
            # Only authenticated users can delete (DELETE) books
            return [IsAuthenticated()]
        return super().get_permissions()   
    
    def get(self, request, id, format=None):
        book= self.get_object(id)
        serializer = BookSerializer(book)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id, format=None):
        book = self.get_object(id)
        serializer = BookSerializer(book, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Book update successful", "data": serializer.data}, status=status.HTTP_202_ACCEPTED)


    def delete(self, request, id, format=None):
        book = self.get_object(id)
        book.delete()
        return Response({"Success": "Book deletion successful"}, status=status.HTTP_204_NO_CONTENT)
    


class AuthorAPIView(APIView):
    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow anyone to view authors
            return [AllowAny()]
        elif self.request.method == 'POST':
            # Only authenticated users can create (POST) authors
            return [IsAuthenticated()]
        return super().get_permissions()
    

    def get(self, request, format=None):
        all_authors = Author.objects.all()
        serializer = AuthorSerializer(all_authors, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

    def post(self, request, format=None):
        new_author = AuthorSerializer(data=request.data)
        new_author.is_valid(raise_exception=True)
        new_author.save()
        return Response({"Success": "Author creation successful"}, status=status.HTTP_201_CREATED)
    


class SingleAuthorAPIView(APIView):
    def get_object(self, id):
        try:
            return Author.objects.get(id=id)
        except Author.DoesNotExist:
            raise Http404
        
    def get_permissions(self):
        if self.request.method == 'GET':
            # Allow anyone to view authors
            return [AllowAny()]
        elif self.request.method == 'PUT':
            # Only authenticated users can update (PUT) authors
            return [IsAuthenticated()]
        elif self.request.method == 'DELETE':
            # Only authenticated users can delete (DELETE) authors
            return [IsAuthenticated()]
        return super().get_permissions()
        
    
    def get(self, request, id, format=None):
        author = self.get_object(id)
        serializer = AuthorSerializer(author)
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    def put(self, request, id, format=None):
        author = self.get_object(id)
        serializer = AuthorSerializer(author, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Author update successful", "data": serializer.data}, status=status.HTTP_202_ACCEPTED)


    def delete(self, request, id, format=None):
        author = self.get_object(id)
        author.delete()
        return Response({"Success": "Author deletion successful"}, status=status.HTTP_204_NO_CONTENT)
    



class AddToFvouriteAPIView(APIView):
    permission_classes = [IsAuthenticated]


    def post(self, request, id, format=None):
       
        def weighted_rating(book, m, C):
            v = book.vote_count
            R = book.vote_average
            return (v / (v + m) * R) + (m / (m + v) * C)     
        

        user_profile = Profile.objects.get(user=request.user)
        
        try:
            book = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return Response({'message': 'Book not found.'}, status=status.HTTP_404_NOT_FOUND)

        if book in user_profile.favourites.all():
            return Response({'message': 'Book is already in your favorites.'}, status=status.HTTP_409_CONFLICT)

        user_profile.favourites.add(book)
        
    
        title = book.title
        book = get_object_or_404(Book, title__iexact=title)

        # Calculate the mean of the vote average for all books
        C = Book.objects.all().aggregate(Avg('vote_average'))['vote_average__avg']

        # Fetch all vote counts from the database (ignoring null values)
        vote_counts = list(Book.objects.filter(vote_count__isnull=False).values_list('vote_count', flat=True))

        # Calculate the 90th percentile using numpy
        if vote_counts:
            m = np.percentile(vote_counts, 90)
        else:
            m = 0  # Fallback if there are no vote counts in the database

        # Filter books that have at least as many votes as 'm'
        qualified_books = Book.objects.filter(vote_count__gte=m, vote_average__isnull=False)

        # Calculate the weighted score for each qualified book and sort by score
        qualified_books = sorted(
            qualified_books, key=lambda x: weighted_rating(x, m, C), reverse=True
        )

        # Render the results to a template
        serializer = BookSerializer(qualified_books, many=True)
        return Response({'message': 'Book added to favorites successfully.', 'Recommended Books': serializer.data}, status=status.HTTP_201_CREATED)


def weighted_rating(book, m, C):
        v = book.vote_count
        R = book.vote_average
        return (v / (v + m) * R) + (m / (m + v) * C)     
    
class RecommenderAPIView(APIView):
    

    def post(self, request, id, format=None):
        book = get_object_or_404(Book, id=id)
        title = book.title
        book = get_object_or_404(Book, title__iexact=title)

        # Calculate the mean of the vote average for all books
        C = Book.objects.all().aggregate(Avg('vote_average'))['vote_average__avg']

        # Fetch all vote counts from the database (ignoring null values)
        vote_counts = list(Book.objects.filter(vote_count__isnull=False).values_list('vote_count', flat=True))

        # Calculate the 90th percentile using numpy
        if vote_counts:
            m = np.percentile(vote_counts, 90)
        else:
            m = 0  # Fallback if there are no vote counts in the database

        # Filter books that have at least as many votes as 'm'
        qualified_books = Book.objects.filter(vote_count__gte=m, vote_average__isnull=False)

        # Calculate the weighted score for each qualified book and sort by score
        qualified_books = sorted(
            qualified_books, key=lambda x: weighted_rating(x, m, C), reverse=True
        )

        # Render the results to a template
        serializer = BookSerializer(qualified_books, many=True)
        return Response({'Recommended Books': serializer.data}, status=status.HTTP_200_OK)
        



class RemoveFavouriteBookView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, id):
        user = request.user

        # Ensure the Profile exists for the current user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Ensure the Book exists
        try:
            book = Book.objects.get(id=id)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Remove the book from the user's favourites
        if book in profile.favourites.all():
            profile.favourites.remove(book)
            return Response({'success': 'Book removed from favourites'}, status=status.HTTP_200_OK)
        else:
            return Response({'error': 'Book not in favourites'}, status=status.HTTP_400_BAD_REQUEST)
        


class SuggestedBooksView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        try:
            profile = Profile.objects.get(user=user)
        except Profile.DoesNotExist:
            return Response({'error': 'Profile not found'}, status=status.HTTP_404_NOT_FOUND)

        favorite_books = profile.favourites.all()
        if not favorite_books.exists():
            return Response({'suggestions': []}, status=status.HTTP_200_OK)

        # Get titles and authors of favorite books
        favorite_titles = [book.title for book in favorite_books]
        favorite_authors = [', '.join([author.full_name for author in book.author.all()]) for book in favorite_books]
        favorite_features = [f"{title} {author}" for title, author in zip(favorite_titles, favorite_authors)]

        # Get all books in the database
        all_books = Book.objects.exclude(id__in=favorite_books.values_list('id', flat=True))
        all_books_features = [f"{book.title} {', '.join([author.full_name for author in book.author.all()])}" for book in all_books]

        # Vectorize the features
        vectorizer = TfidfVectorizer()
        tfidf_matrix = vectorizer.fit_transform(favorite_features + all_books_features)

        # Compute similarity scores
        cosine_similarities = linear_kernel(tfidf_matrix[:len(favorite_books)], tfidf_matrix[len(favorite_books):])
        book_similarity_scores = cosine_similarities.mean(axis=0)
        top_indices = book_similarity_scores.argsort()[-5:][::-1]

        # Convert top_indices to standard Python integers
        top_indices = [int(index) for index in top_indices]

        # Fetch the recommended books using the converted indices
        recommended_books = [all_books[index] for index in top_indices]

        serializer = BookSerializer(recommended_books, many=True)
        return Response({'suggestions': serializer.data}, status=status.HTTP_200_OK)



