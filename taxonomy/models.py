from django.db import models
from django.utils.text import slugify

from wagtail.admin.panels import FieldPanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.fields import RichTextField


@register_snippet
class Category(models.Model):
    """
    General-purpose categories that can be applied to any content type.
    Examples: Product categories, blog categories, resource types, etc.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Category name (e.g., 'Electronics', 'Software', 'Tutorial')"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name"
    )
    description = RichTextField(
        blank=True,
        help_text="Category description"
    )
    
    # Hierarchy - allows nested categories
    parent = models.ForeignKey(
        'self',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='children',
        help_text="Parent category (leave blank for top-level)"
    )
    
    # Visual
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon class or emoji (e.g., 'fa-laptop', '💻')"
    )
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code (e.g., '#FF5733')"
    )
    image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+',
        help_text="Category image/thumbnail"
    )
    
    # Display
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Show this category on the website"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('description'),
        ], heading="Basic Information"),
        
        MultiFieldPanel([
            FieldPanel('parent'),
        ], heading="Hierarchy"),
        
        MultiFieldPanel([
            FieldPanel('icon'),
            FieldPanel('color'),
            FieldPanel('image'),
        ], heading="Visual Design"),
        
        MultiFieldPanel([
            FieldPanel('display_order'),
            FieldPanel('is_active'),
        ], heading="Display Settings"),
    ]
    
    api_fields = [
        APIField('name'),
        APIField('slug'),
        APIField('description'),
        APIField('parent'),
        APIField('icon'),
        APIField('color'),
        APIField('image'),
        APIField('display_order'),
        APIField('is_active'),
    ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        if self.parent:
            return f"{self.parent.name} > {self.name}"
        return self.name
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Category"
        verbose_name_plural = "Categories"


@register_snippet
class Tag(models.Model):
    """
    Flexible tags that can be applied to any content type.
    Tags are more specific than categories and allow free-form organization.
    """
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="Tag name (e.g., 'AI', 'Machine Learning', 'Python')"
    )
    slug = models.SlugField(
        max_length=100,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of this tag"
    )
    
    # Visual
    color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Hex color code for tag display (e.g., '#3B82F6')"
    )
    
    # Usage tracking
    use_count = models.IntegerField(
        default=0,
        editable=False,
        help_text="Number of times this tag has been used"
    )
    
    # Display
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this tag (e.g., show in tag cloud)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Allow this tag to be used"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('slug'),
        FieldPanel('description'),
        FieldPanel('color'),
        
        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_active'),
        ], heading="Display Settings"),
    ]
    
    api_fields = [
        APIField('name'),
        APIField('slug'),
        APIField('description'),
        APIField('color'),
        APIField('use_count'),
        APIField('is_featured'),
        APIField('is_active'),
    ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['-use_count', 'name']
        verbose_name = "Tag"
        verbose_name_plural = "Tags"


@register_snippet
class Badge(models.Model):
    """
    Badges/labels that can be applied to products, content, or users.
    Examples: 'New', 'Featured', 'Best Seller', 'Editor's Choice', 'Premium'
    """
    
    BADGE_TYPE_CHOICES = [
        ('status', 'Status'),           # New, Draft, Published
        ('quality', 'Quality'),         # Featured, Premium, Verified
        ('popularity', 'Popularity'),   # Best Seller, Trending, Hot
        ('achievement', 'Achievement'), # Award Winner, Top Rated
        ('special', 'Special Offer'),   # Sale, Limited Edition
        ('custom', 'Custom'),           # Other/Custom
    ]
    
    BADGE_STYLE_CHOICES = [
        ('default', 'Default'),
        ('primary', 'Primary'),
        ('secondary', 'Secondary'),
        ('success', 'Success'),
        ('warning', 'Warning'),
        ('danger', 'Danger'),
        ('info', 'Info'),
    ]
    
    name = models.CharField(
        max_length=50,
        unique=True,
        help_text="Badge name (e.g., 'New', 'Featured', 'Best Seller')"
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        blank=True,
        help_text="URL-friendly version of the name"
    )
    
    badge_type = models.CharField(
        max_length=20,
        choices=BADGE_TYPE_CHOICES,
        default='custom',
        help_text="Type/purpose of this badge"
    )
    
    description = models.TextField(
        blank=True,
        help_text="What this badge represents"
    )
    
    # Visual Design
    style = models.CharField(
        max_length=20,
        choices=BADGE_STYLE_CHOICES,
        default='default',
        help_text="Visual style preset"
    )
    icon = models.CharField(
        max_length=100,
        blank=True,
        help_text="Icon class or emoji (e.g., 'fa-star', '⭐')"
    )
    background_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Background color hex code (e.g., '#10B981')"
    )
    text_color = models.CharField(
        max_length=7,
        blank=True,
        help_text="Text color hex code (e.g., '#FFFFFF')"
    )
    
    # Display Settings
    display_order = models.IntegerField(
        default=0,
        help_text="Priority order (lower numbers appear first)"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Allow this badge to be used"
    )
    
    # Auto-expiration (optional)
    expires_at = models.DateTimeField(
        null=True,
        blank=True,
        help_text="Auto-hide this badge after this date (optional)"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    panels = [
        MultiFieldPanel([
            FieldPanel('name'),
            FieldPanel('slug'),
            FieldPanel('badge_type'),
            FieldPanel('description'),
        ], heading="Basic Information"),
        
        MultiFieldPanel([
            FieldPanel('style'),
            FieldPanel('icon'),
            FieldPanel('background_color'),
            FieldPanel('text_color'),
        ], heading="Visual Design"),
        
        MultiFieldPanel([
            FieldPanel('display_order'),
            FieldPanel('is_active'),
            FieldPanel('expires_at'),
        ], heading="Display Settings"),
    ]
    
    api_fields = [
        APIField('name'),
        APIField('slug'),
        APIField('badge_type'),
        APIField('description'),
        APIField('style'),
        APIField('icon'),
        APIField('background_color'),
        APIField('text_color'),
        APIField('display_order'),
        APIField('is_active'),
        APIField('is_expired'),
    ]
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if badge has expired"""
        if self.expires_at:
            from django.utils import timezone
            return timezone.now() > self.expires_at
        return False
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Badge"
        verbose_name_plural = "Badges"
