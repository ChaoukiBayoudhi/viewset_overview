from operator import index
from django import db
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator, MinLengthValidator, RegexValidator
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import re
from django.db.models import F, Q, CheckConstraint, UniqueConstraint

def validate_no_special_chars(value):
    if re.search(r'[!@#$%^&*()_+=\[\]{}|\\;:"<>?]', value):
        raise ValidationError(
            _('%(value)s contains special characters. Only alphanumeric characters, spaces, and hyphens are allowed.'),
            params={'value': value},
        )

def validate_hierarchical_integrity(parent):
    """Prevent circular references in category hierarchy"""
    if parent is None:
        return
    
    # Check if this would create a circular reference
    current = parent
    while current is not None:
        if current.parent_id == parent.id:
            raise ValidationError(_('This would create a circular reference in the category hierarchy.'))
        current = current.parent

class Publisher(models.Model):
    name = models.CharField(max_length=255)
    website = models.URLField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        db_table = 'publisher'

class Author(models.Model):
    name = models.CharField(max_length=255)
    biography = models.TextField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        db_table = 'author'

class Category(models.Model):
    name = models.CharField(
        max_length=100,
        validators=[
            MinLengthValidator(2, message=_("Category name must be at least 2 characters long")),
            RegexValidator(
                regex=r'^[A-Za-z0-9\s\-]+$',
                message=_("Category name can only contain alphanumeric characters, spaces, and hyphens"),
            ),
            validate_no_special_chars,
        ]
    )
    description = models.TextField(blank=True, null=True)
    parent = models.ForeignKey(
        'self', 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='subcategories'
    )
    slug = models.SlugField(
        max_length=120, 
        unique=True,
        help_text=_("URL-friendly version of the category name")
    )
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    display_order = models.PositiveIntegerField(
        default=0,
        validators=[MaxValueValidator(1000)],
        help_text=_("Order in which category appears (0-1000)")
    )
    
    def __str__(self):
        return self.name
    
    def clean(self):
        """Custom model validation"""
        # Prevent a category from being its own parent
        if self.id and self.parent_id == self.id:
            raise ValidationError(_("A category cannot be its own parent."))
        
        # Check for circular references
        if self.parent:
            validate_hierarchical_integrity(self.parent)
        
        # Ensure parent categories with children cannot be deactivated
        if self.id and not self.is_active and self.subcategories.filter(is_active=True).exists():
            raise ValidationError(_("Cannot deactivate a category that has active subcategories."))
    
    def get_full_path(self):
        """Return the full hierarchical path of the category"""
        if self.parent:
            return f"{self.parent.get_full_path()} > {self.name}"
        return self.name
    
    def get_all_subcategories(self):
        """Return all subcategories recursively"""
        result = []
        for subcategory in self.subcategories.all():
            result.append(subcategory)
            result.extend(subcategory.get_all_subcategories())
        return result
    
    class Meta:
        ordering = ['display_order', 'name']
        db_table = 'category'
        verbose_name_plural = 'categories'
        constraints = [
            models.CheckConstraint(
                check=~models.Q(id=models.F('parent')),
                name='prevent_self_parent'
            ),
        ]

class Book(models.Model):
    LANGUAGE_CHOICES = [
        ('EN', 'English'),
        ('FR', 'French'),
        ('ES', 'Spanish'),
        ('DE', 'German'),
        ('ZH', 'Chinese'),
        ('JA', 'Japanese'),
        ('AR', 'Arabic'),
    ]
    
    title = models.CharField(max_length=255)
    author = models.CharField(max_length=255)
    authors = models.ManyToManyField(Author, related_name='books')
    published_date = models.DateField()
    isbn = models.CharField(max_length=13, unique=True)
    genre = models.CharField(max_length=100)
    summary = models.TextField(blank=True, null=True)
    
    # New fields
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, related_name='books')
    page_count = models.PositiveIntegerField(blank=True, null=True)
    language = models.CharField(max_length=2, choices=LANGUAGE_CHOICES, default='EN')
    price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    cover_image = models.ImageField(upload_to='book_covers/', blank=True, null=True)
    rating = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(5)], blank=True, null=True)
    is_bestseller = models.BooleanField(default=False)
    
    # Many-to-many with through model
    categories = models.ManyToManyField(Category, through='BookCategory', related_name='books')

    def __str__(self):
        return self.title
    
    def is_long_book(self):
        """Return True if the book has more than 500 pages"""
        if self.page_count and self.page_count > 500:
            return True
        return False
    
    def get_authors_display(self):
        """Return a comma-separated list of author names"""
        return ", ".join([author.name for author in self.authors.all()])

    class Meta:
        ordering = ['title']
        db_table = 'book'
        constraints = [
            models.UniqueConstraint(fields=['title', 'author'], name='unique_book'),
            models.CheckConstraint(check=models.Q(isbn__regex=r'^\d{13}$'), name='isbn_length'),
            models.CheckConstraint(check=models.Q(rating__gte=0, rating__lte=5), name='rating_range'),
            models.CheckConstraint(check=models.Q(price__gte=0), name='price_non_negative'),
            # Add a constraint for page count
            models.CheckConstraint(check=models.Q(page_count__gte=1) | models.Q(page_count__isnull=True), 
                                  name='page_count_positive'),
        ]
        indexes = [
            models.Index(fields=['title']),
            models.Index(fields=['author']),
            models.Index(fields=['published_date']),
            models.Index(fields=['isbn']),
            models.Index(fields=['genre']),
            # Add index for publisher and bestseller status for faster queries
            models.Index(fields=['publisher', 'is_bestseller']),
            models.Index(fields=['language']),
        ]

class BookCategory(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE)
    added_date = models.DateTimeField(auto_now_add=True)
    primary = models.BooleanField(default=False, help_text="Indicates if this is the primary category for the book")
    relevance_score = models.FloatField(validators=[MinValueValidator(0), MaxValueValidator(10)], 
                                       default=5, help_text="How relevant this category is to the book (0-10)")
    
    def __str__(self):
        return f"{self.book.title} - {self.category.name}"
    
    def clean(self):
        """Ensure only one primary category per book"""
        if self.primary and BookCategory.objects.filter(book=self.book, primary=True).exclude(pk=self.pk).exists():
            raise ValidationError(_("A book can have only one primary category."))
    
    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)
    
    class Meta:
        db_table = 'book_category'
        unique_together = ['book', 'category']
        ordering = ['-primary', '-relevance_score']
        verbose_name_plural = 'book categories'
        constraints = [
            # Ensure relevance score is within range at database level
            models.CheckConstraint(check=models.Q(relevance_score__gte=0, relevance_score__lte=10), 
                                  name='relevance_score_range'),
            # Ensure only one primary category per book
            models.UniqueConstraint(
                fields=['book'],
                condition=models.Q(primary=True),
                name='unique_primary_category_per_book'
            ),
        ]

class Review(models.Model):
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='reviews')
    reviewer_name = models.CharField(max_length=255)
    content = models.TextField()
    rating = models.PositiveSmallIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Review for {self.book.title} by {self.reviewer_name}"
    
    class Meta:
        ordering = ['-created_at']
        db_table = 'review'
        constraints = [
            # Ensure rating is within range at database level
            models.CheckConstraint(check=models.Q(rating__gte=1, rating__lte=5), 
                                  name='review_rating_range'),
        ]
        indexes = [
            # Add index for book and rating for faster queries
            models.Index(fields=['book', 'rating']),
            models.Index(fields=['created_at']),
        ]
        
