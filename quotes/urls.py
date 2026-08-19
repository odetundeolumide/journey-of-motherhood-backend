from django.urls import path
from .views import ListQuoteView, DetailQuoteView

urlpatterns = [
    path('', ListQuoteView.as_view(), name="quote_list"),
    path('<int:pk>/', DetailQuoteView.as_view(), name="quote_detail")
]
