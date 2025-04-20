from django.urls import path, include
from rest_framework import routers
from .views import (
    BookViewSet,
    AuthorViewSet,
    PublisherViewSet,
    CategoryViewSet,
    BookCategoryViewSet,
    ReviewViewSet,
)

router = routers.DefaultRouter()
router.register(r'books', BookViewSet)
router.register(r'authors', AuthorViewSet)
router.register(r'publishers', PublisherViewSet)
router.register(r'categories', CategoryViewSet)
router.register(r'book-categories', BookCategoryViewSet)
router.register(r'reviews', ReviewViewSet)

urlpatterns = [
    path('', include(router.urls)),
]