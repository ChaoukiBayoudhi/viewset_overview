# Import the serializers module from Django REST framework
# This module provides the base serializer classes we'll extend
from rest_framework import serializers
# Import all the models we'll be creating serializers for
from .models import Book, Author, Publisher, Category, Review, BookCategory

class PublisherSerializer(serializers.ModelSerializer):
    """
    Serializer for the Publisher model.
    ModelSerializer automatically creates fields based on the model.
    """
    class Meta:
        # Specify which model this serializer is for
        model = Publisher
        # '__all__' means include all fields from the model
        fields = '__all__'

class AuthorSerializer(serializers.ModelSerializer):
    """
    Serializer for the Author model.
    Converts Author model instances into JSON representations and vice versa.
    """
    class Meta:
        model = Author
        fields = '__all__'

class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the Category model with additional computed fields.
    """
    # ReadOnlyField creates a field that's derived from the model but not directly mapped
    # source='parent.name' means: get the 'name' attribute from the 'parent' relation
    # allow_null=True means: don't error if parent is None
    parent_name = serializers.ReadOnlyField(source='parent.name', allow_null=True)
    
    # SerializerMethodField creates a field whose value comes from a method
    # The method must be named get_<field_name>
    subcategory_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = '__all__'
    
    def get_subcategory_count(self, obj):
        """
        Calculate the number of subcategories for this category.
        
        Args:
            obj: The Category instance being serialized
            
        Returns:
            int: The count of subcategories
        """
        # Access the reverse relation 'subcategories' and count the results
        return obj.subcategories.count()

class ReviewSerializer(serializers.ModelSerializer):
    """
    Serializer for the Review model with an additional field for the book title.
    """
    # This adds the book's title as a read-only field to the serialized output
    book_title = serializers.ReadOnlyField(source='book.title')
    
    class Meta:
        model = Review
        fields = '__all__'

class BookCategorySerializer(serializers.ModelSerializer):
    """
    Serializer for the BookCategory model (the through model for the many-to-many
    relationship between Book and Category).
    """
    # Add readable names for the related objects
    category_name = serializers.ReadOnlyField(source='category.name')
    book_title = serializers.ReadOnlyField(source='book.title')
    
    class Meta:
        model = BookCategory
        fields = '__all__'

class BookSerializer(serializers.ModelSerializer):
    """
    Serializer for the Book model with additional computed fields to provide
    rich information about related objects.
    """
    # Add the publisher name as a read-only field
    publisher_name = serializers.ReadOnlyField(source='publisher.name', allow_null=True)
    
    # These fields require custom logic, so we use SerializerMethodField
    author_names = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    average_rating = serializers.SerializerMethodField()
    categories_list = serializers.SerializerMethodField()
    
    class Meta:
        model = Book
        fields = '__all__'
    
    def get_author_names(self, obj):
        """
        Get a list of author names for this book.
        
        Args:
            obj: The Book instance being serialized
            
        Returns:
            list: A list of author names
        """
        # Query the many-to-many relationship and extract just the names
        return [author.name for author in obj.authors.all()]
    
    def get_review_count(self, obj):
        """
        Count the number of reviews for this book.
        
        Args:
            obj: The Book instance being serialized
            
        Returns:
            int: The count of reviews
        """
        # Count the related reviews using the reverse relation name
        return obj.reviews.count()
    
    def get_average_rating(self, obj):
        """
        Calculate the average rating for this book.
        
        Args:
            obj: The Book instance being serialized
            
        Returns:
            float or None: The average rating, or None if no reviews exist
        """
        # Get all reviews for this book
        reviews = obj.reviews.all()
        # If there are no reviews, return None
        if not reviews:
            return None
        # Calculate the average rating
        return sum(review.rating for review in reviews) / reviews.count()
    
    def get_categories_list(self, obj):
        """
        Get a list of categories with additional information from the through model.
        
        Args:
            obj: The Book instance being serialized
            
        Returns:
            list: A list of dictionaries containing category information
        """
        # Query the through model to get all book-category relationships
        book_categories = BookCategory.objects.filter(book=obj)
        # Create a list of dictionaries with the desired information
        return [
            {
                'id': bc.category.id,
                'name': bc.category.name,
                'primary': bc.primary,
                'relevance_score': bc.relevance_score
            }
            for bc in book_categories
        ]

class BookDetailSerializer(BookSerializer):
    """
    Extended serializer for detailed Book views.
    Inherits all fields and methods from BookSerializer and adds nested serializers
    for related models to provide complete information in a single API response.
    """
    # Include full review objects instead of just counts
    # many=True indicates this is a one-to-many relationship
    # read_only=True means these fields are not used for updates
    reviews = ReviewSerializer(many=True, read_only=True)
    
    # Include the full publisher object
    publisher = PublisherSerializer(read_only=True)
    
    # Include full author objects
    authors = AuthorSerializer(many=True, read_only=True)
    
    class Meta:
        model = Book
        fields = '__all__'