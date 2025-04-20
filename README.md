# Django REST Framework ViewSet Overview

A comprehensive demonstration of Django REST Framework ViewSets using a book management system. This project showcases best practices for building RESTful APIs with Django.

## Features

- Complete CRUD operations for books, authors, publishers, categories, and reviews
- Advanced serialization with nested relationships
- JWT Authentication
- API documentation with Swagger/OpenAPI (drf-yasg)
- PostgreSQL database integration
- Production-ready with Gunicorn and Whitenoise

## Models

- **Book**: Core entity with title, publication date, ISBN, etc.
- **Author**: Book creators with biographical information
- **Publisher**: Publishing companies
- **Category**: Hierarchical book categories with parent-child relationships
- **Review**: User reviews and ratings for books
- **BookCategory**: Through model for book-category relationships with additional metadata

## Installation

1. Clone the repository
```bash
git clone https://github.com/ChaoukiBayoudhi/viewset_overview.git
cd viewset_overview