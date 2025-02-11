from django.contrib import admin
from .models import Book, Review  # ✅ Ensure Review is correctly imported

# ✅ Check if Book is already registered before registering
if not admin.site.is_registered(Book):
    @admin.register(Book)
    class BookAdmin(admin.ModelAdmin):
        list_display = ('title', 'author', 'genre', 'created_at')
        search_fields = ('title', 'author', 'genre')

# ✅ Check if Review is already registered before registering
if not admin.site.is_registered(Review):
    @admin.register(Review)
    class ReviewAdmin(admin.ModelAdmin):
        list_display = ('book', 'user', 'rating', 'created_at')
        search_fields = ('book__title', 'user__username')
