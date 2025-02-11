
import os
from dotenv import load_dotenv

load_dotenv()  # Load environment variables
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")



from django.shortcuts import render, get_object_or_404
from .models import Book  # Ensure the Book model is imported
from django.db.models import Q
from .forms import ReviewForm  # Make sure this is now correct



# Home Page View
def home(request):
    return render(request, 'recommendations/home.html')


# Book List View with Improved Search (Title, Author, Genre)
def book_list(request):
    query = request.GET.get("q", "")  # Get search query
    books = Book.objects.all()  # Fetch all books

    if query:
        books = books.filter(
            Q(title__icontains=query) | 
            Q(author__icontains=query) | 
            Q(genre__icontains=query)
        )  # Case-insensitive search across title, author, and genre

    return render(request, 'recommendations/book_list.html', {'books': books})

# Book Detail View
from django.shortcuts import render, get_object_or_404
from .models import Book

# ✅ Updated Book Detail View to Pass Recommendations
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from recommendations.models import Book, Review
from .forms import ReviewForm

def book_detail(request, pk):
    book = get_object_or_404(Book, pk=pk)
    reviews = book.reviews.all()
    form = ReviewForm()

    if request.method == "POST":
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.book = book
            review.user = request.user
            review.save()
            return redirect('recommendations:book_detail', pk=pk)

    return render(request, 'recommendations/book_detail.html', {
        'book': book,
        'reviews': reviews,
        'form': form
    })

import os
import requests
from dotenv import load_dotenv
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Book

# ✅ Load environment variables
load_dotenv()
HUGGINGFACE_API_KEY = os.getenv("HUGGINGFACE_API_KEY")

@csrf_exempt
def generate_summary(request, pk):
    book = Book.objects.get(pk=pk)
    
    url = "https://api-inference.huggingface.co/models/facebook/bart-large-cnn"  # Example summarization model
    
    headers = {
        "Authorization": f"Bearer {HUGGINGFACE_API_KEY}"
    }
    
    payload = {
        "inputs": f"Summarize the book '{book.title}' by {book.author}: {book.description}"
    }

    try:
        response = requests.post(url, headers=headers, json=payload)

        if response.status_code == 200:
            summary = response.json()[0]['summary_text']
            book.summary = summary
            book.save()
            return JsonResponse({'summary': summary})
        else:
            return JsonResponse({'error': f"API Error: {response.json()}"}, status=500)

    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)



from django.shortcuts import render, get_object_or_404
from .models import Book
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np

def book_recommendations(request, pk):
    book = get_object_or_404(Book, pk=pk)
    
    # Get all books except the current one
    books = Book.objects.exclude(pk=pk)
    
    if not books.exists():
        return render(request, 'recommendations/book_recommendations.html', {
            'book': book,
            'recommended_books': [],
        })

    # Convert book descriptions into vectors
    descriptions = [book.description for book in books]
    descriptions.insert(0, book.description)  # Add the selected book's description at index 0

    vectorizer = TfidfVectorizer(stop_words='english')
    tfidf_matrix = vectorizer.fit_transform(descriptions)

    # Compute cosine similarity
    similarity_matrix = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
    similarity_scores = similarity_matrix.flatten()

    # Get indices of top similar books
    recommended_indices = np.argsort(similarity_scores)[::-1][:5]  # Get top 5 recommendations

    # ✅ Fix: Convert indices to Python int before filtering
    recommended_books = Book.objects.filter(id__in=[int(idx) for idx in recommended_indices])

    return render(request, 'recommendations/book_recommendations.html', {
        'book': book,
        'recommended_books': recommended_books
    })



# 📌 Add Review View
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from .models import Book, Review
from django.contrib import messages

# 📌 Add Review View
@login_required
def add_review(request, pk):
    book = get_object_or_404(Book, pk=pk)

    if request.method == "POST":
        rating = request.POST.get("rating")
        comment = request.POST.get("comment")

        if not rating or not comment:
            messages.error(request, "Please fill in all fields.")
            return redirect("recommendations:book_detail", pk=book.pk)

        # Save Review
        Review.objects.create(
            book=book,
            user=request.user,
            rating=int(rating),
            comment=comment,
        )
        messages.success(request, "Your review has been added successfully!")
        return redirect("recommendations:book_detail", pk=book.pk)

    return redirect("recommendations:book_detail", pk=book.pk)



 
