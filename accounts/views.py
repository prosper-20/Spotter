from django.shortcuts import render
from rest_framework.views import APIView
from .serializers import CustomUserRegistrationSerializer
from rest_framework.response import Response
from rest_framework import status
from library.models import Book
from rest_framework.permissions import IsAuthenticated

class RegistrationAPIView(APIView):
    def post(self, reuqest, fomrat=None):
        serializer = CustomUserRegistrationSerializer(data=reuqest.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({"Success": "Account creation successful",
                         "data": serializer.data
                         }, status=status.HTTP_201_CREATED)
    



