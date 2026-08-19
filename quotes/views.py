from django.shortcuts import render
from rest_framework import generics

from quotes.serializers import QuoteSerializer
from .models import Quote
# Create your views here.

class ListQuoteView(generics.ListAPIView):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer


class DetailQuoteView(generics.RetrieveAPIView):
    queryset = Quote.objects.all()
    serializer_class = QuoteSerializer