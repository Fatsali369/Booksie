from django.urls import path
from .views import home, book_list, book_detail, book_recommendations, add_review, generate_summary

app_name = "recommendations"

urlpatterns = [
    path("", home, name="home"),
    path("books/", book_list, name="book_list"),
    path("books/<int:pk>/", book_detail, name="book_detail"),
    path("books/<int:pk>/recommendations/", book_recommendations, name="book_recommendations"),
    path("books/<int:pk>/add_review/", add_review, name="add_review"),
    path("books/<int:pk>/generate_summary/", generate_summary, name="generate_summary"),  # New AI route
]
