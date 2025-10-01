from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.fields import RichTextField


@register_snippet
class FAQCategory(models.Model):
    """Categories for organizing FAQ items"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g., 'General', 'Billing', 'Technical Support'"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of this category"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
        FieldPanel('display_order'),
    ]
    
    api_fields = [
        APIField('name'),
        APIField('description'),
        APIField('display_order'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "FAQ Category"
        verbose_name_plural = "FAQ Categories"


@register_snippet
class FAQItem(models.Model):
    """Individual FAQ question and answer"""
    
    question = models.CharField(
        max_length=500,
        help_text="The question being asked"
    )
    answer = RichTextField(
        help_text="The answer to the question (supports rich text)"
    )
    
    category = models.ForeignKey(
        'FAQCategory',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='faq_items',
        help_text="Categorize this FAQ item"
    )
    
    # Display Settings
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this FAQ (e.g., show on homepage)"
    )
    is_published = models.BooleanField(
        default=True,
        help_text="Show this FAQ on the website"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    
    # Metadata
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    # SEO
    slug = models.SlugField(
        max_length=255,
        blank=True,
        help_text="URL-friendly version of the question (optional)"
    )
    
    panels = [
        FieldPanel('question'),
        FieldPanel('answer'),
        FieldPanel('category'),
        
        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_published'),
            FieldPanel('display_order'),
        ], heading="Display Settings"),
        
        FieldPanel('slug'),
    ]
    
    api_fields = [
        APIField('question'),
        APIField('answer'),
        APIField('category'),
        APIField('is_featured'),
        APIField('is_published'),
        APIField('display_order'),
        APIField('slug'),
        APIField('created_at'),
        APIField('updated_at'),
    ]
    
    def save(self, *args, **kwargs):
        # Auto-generate slug if not provided
        if not self.slug:
            from django.utils.text import slugify
            self.slug = slugify(self.question[:100])
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.question
    
    class Meta:
        ordering = ['category', 'display_order', 'question']
        verbose_name = "FAQ Item"
        verbose_name_plural = "FAQ Items"


@register_snippet
class FAQCollection(ClusterableModel):
    """A curated collection of FAQ items for specific pages or sections"""
    
    title = models.CharField(
        max_length=200,
        help_text="Name for this FAQ collection (e.g., 'Homepage FAQs', 'Product FAQs')"
    )
    description = models.TextField(
        blank=True,
        help_text="Optional description of this collection"
    )
    
    panels = [
        FieldPanel('title'),
        FieldPanel('description'),
        InlinePanel('collection_items', label="FAQ Items"),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('description'),
        APIField('collection_items'),
    ]
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "FAQ Collection"
        verbose_name_plural = "FAQ Collections"


class FAQCollectionItem(Orderable):
    """Links FAQ items to collections"""
    
    collection = ParentalKey(
        'FAQCollection',
        related_name='collection_items',
        on_delete=models.CASCADE
    )
    
    faq_item = models.ForeignKey(
        'FAQItem',
        on_delete=models.CASCADE,
        related_name='+'
    )
    
    panels = [
        FieldPanel('faq_item'),
    ]
    
    api_fields = [
        APIField('faq_item'),
    ]
    
    def __str__(self):
        return f"{self.collection.title} - {self.faq_item.question}"
