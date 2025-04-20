# Django REST Framework ViewSet Overview

A comprehensive demonstration of Django REST Framework ViewSets using a book management system. This project showcases best practices for building RESTful APIs with Django.

## Features

- Complete CRUD operations for books, authors, publishers, categories, and reviews
- Advanced serialization with nested relationships
- JWT Authentication
- API documentation with Swagger/OpenAPI (drf-yasg)
- PostgreSQL database integration
- Production-ready with Gunicorn and Whitenoise
- Hierarchical data modeling with parent-child relationships
- Detailed filtering, searching, and ordering capabilities
- Nested serializers for complex data representation
- Custom pagination

## Models

- **Book**: Core entity with title, publication date, ISBN, etc.
- **Author**: Book creators with biographical information
- **Publisher**: Publishing companies
- **Category**: Hierarchical book categories with parent-child relationships
- **Review**: User reviews and ratings for books
- **BookCategory**: Through model for book-category relationships with additional metadata

## Installation

1. **Clone the repository**
    ```bash
    git clone https://github.com/ChaoukiBayoudhi/viewset_overview.git
    cd viewset_overview
    ```

2. **Set up pipenv environment**
    ```bash
    # Install pipenv if you don't have it
    pip install pipenv

    # Create virtual environment and activate it
    pipenv shell
    ```

3. **Install dependencies**
    ```bash
    pipenv install -r requirements.txt
    ```

4. **Configure the database**
    - Edit `settings.py` to set your PostgreSQL credentials and database name.

5. **Run migrations**
    ```bash
    python manage.py makemigrations
    python manage.py migrate
    ```

6. **Create a superuser**
    ```bash
    python manage.py createsuperuser
    ```

7. **Start the development server**
    ```bash
    python manage.py runserver
    ```

8. **Access the application**
    - Admin interface: [http://127.0.0.1:8000/admin/](http://127.0.0.1:8000/admin/)
    - API documentation: [http://127.0.0.1:8000/swagger/](http://127.0.0.1:8000/swagger/)
    - API root: [http://127.0.0.1:8000/api/](http://127.0.0.1:8000/api/)

## API Endpoints

- `/api/books/` - Book management (list, create, retrieve, update, delete)
- `/api/authors/` - Author management
- `/api/publishers/` - Publisher management
- `/api/categories/` - Category management
- `/api/reviews/` - Review management
- `/api/book-categories/` - Book-category relationship management

## Example Usage

### Obtain JWT Token

```bash
curl -X POST http://localhost:8000/api/token/ \
  -H "Content-Type: application/json" \
  -d '{"username": "admin", "password": "yourpassword"}'
```
### Use JWT Token
```bash
curl -X GET hse JWT Token
```bash
curl -X GET URL_ADDRESS:8000/api/books/ \
  -H "Authorization: Bearer <your_jwt_token>"
```
### Create a Book
```bash
curl -X POST eate a Book
```bash
curl -X POST URL_ADDRESS:8000/api/books/ \
  -H "Authorization: Bearer <your_jwt_token>" \
  -H "Content-Type: application/json" \
  -d '{"title": "New Book", "publication_date": "2023-01-01", "isbn": "1234567890"}'
```
## License
This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.

## Author
[Chaouki Bayoudhi]
