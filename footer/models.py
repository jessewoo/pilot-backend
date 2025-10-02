from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.models import Orderable
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


@register_snippet
class Footer(ClusterableModel):
    """Main footer content with company info and links"""
    
    title = models.CharField(
        max_length=100,
        help_text="Internal name for this footer (e.g., 'Main Footer')"
    )
    
    # Company Information
    company_name = models.CharField(max_length=200, blank=True)
    tagline = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short company tagline or description"
    )
    description = models.TextField(
        blank=True,
        help_text="About the company (short paragraph)"
    )
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    zip_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True)
    
    # Legal & Misc
    copyright_text = models.CharField(
        max_length=255,
        blank=True,
        help_text="e.g., '© 2025 Company Name. All rights reserved.'"
    )

    # Flexible Content Sections
    content_sections = StreamField([
        ('text_section', blocks.StructBlock([
            ('title', blocks.CharBlock(required=False)),
            ('content', blocks.RichTextBlock()),
        ], icon='doc-full')),

        ('link_list', blocks.StructBlock([
            ('title', blocks.CharBlock(required=False)),
            ('links', blocks.ListBlock(
                blocks.StructBlock([
                    ('text', blocks.CharBlock()),
                    ('url', blocks.URLBlock()),
                    ('open_in_new_tab', blocks.BooleanBlock(required=False, default=False)),
                ])
            )),
        ], icon='list-ul')),

        ('image_section', blocks.StructBlock([
            ('image', ImageChooserBlock()),
            ('alt_text', blocks.CharBlock(required=False)),
            ('caption', blocks.CharBlock(required=False)),
            ('link', blocks.URLBlock(required=False)),
        ], icon='image')),

        ('contact_info', blocks.StructBlock([
            ('title', blocks.CharBlock(required=False)),
            ('items', blocks.ListBlock(
                blocks.StructBlock([
                    ('label', blocks.CharBlock()),
                    ('value', blocks.CharBlock()),
                    ('icon', blocks.CharBlock(required=False, help_text="Icon class or emoji")),
                ])
            )),
        ], icon='mail')),

        ('newsletter_signup', blocks.StructBlock([
            ('title', blocks.CharBlock(default="Subscribe to our newsletter")),
            ('description', blocks.TextBlock(required=False)),
            ('placeholder', blocks.CharBlock(default="Enter your email")),
            ('button_text', blocks.CharBlock(default="Subscribe")),
            ('action_url', blocks.URLBlock(help_text="Form submission URL")),
        ], icon='mail')),

        ('custom_html', blocks.RawHTMLBlock(icon='code')),

    ], use_json_field=True, blank=True)

    panels = [
        FieldPanel('title'),
        
        MultiFieldPanel([
            FieldPanel('company_name'),
            FieldPanel('tagline'),
            FieldPanel('description'),
        ], heading="Company Information"),
        
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone'),
            FieldPanel('address_line_1'),
            FieldPanel('address_line_2'),
            FieldPanel('city'),
            FieldPanel('state'),
            FieldPanel('zip_code'),
            FieldPanel('country'),
        ], heading="Contact Information"),
        
        MultiFieldPanel([
            FieldPanel('copyright_text'),
        ], heading="Legal"),

        FieldPanel('content_sections'),

        InlinePanel('footer_columns', label="Footer Link Columns"),
        InlinePanel('social_links', label="Social Media Links"),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('company_name'),
        APIField('tagline'),
        APIField('description'),
        APIField('email'),
        APIField('phone'),
        APIField('address_line_1'),
        APIField('address_line_2'),
        APIField('city'),
        APIField('state'),
        APIField('zip_code'),
        APIField('country'),
        APIField('copyright_text'),
        APIField('content_sections'),
        APIField('footer_columns'),
        APIField('social_links'),
    ]
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Footer"
        verbose_name_plural = "Footers"


class FooterColumn(ClusterableModel, Orderable):
    """A column of links in the footer (e.g., 'Quick Links', 'Resources', 'Legal')"""

    footer = ParentalKey(
        'Footer',
        related_name='footer_columns',
        on_delete=models.CASCADE
    )
    
    title = models.CharField(
        max_length=100,
        help_text="Column heading (e.g., 'Quick Links', 'Resources')"
    )
    
    panels = [
        FieldPanel('title'),
        InlinePanel('column_links', label="Links"),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('column_links'),
    ]
    
    def __str__(self):
        return self.title


class FooterLink(Orderable):
    """Individual link within a footer column"""
    
    column = ParentalKey(
        'FooterColumn',
        related_name='column_links',
        on_delete=models.CASCADE
    )
    
    title = models.CharField(max_length=100)
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.CASCADE,
        help_text="Link to an internal page"
    )
    link_url = models.URLField(
        blank=True,
        help_text="Or link to an external URL"
    )
    open_in_new_tab = models.BooleanField(default=False)
    
    panels = [
        FieldPanel('title'),
        FieldPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('open_in_new_tab'),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('link_page'),
        APIField('link_url'),
        APIField('open_in_new_tab'),
    ]
    
    @property
    def link(self):
        """Return the appropriate link (page or URL)"""
        if self.link_page:
            return self.link_page.url
        return self.link_url
    
    def __str__(self):
        return self.title


class SocialMediaLink(Orderable):
    """Social media links for the footer"""
    
    PLATFORM_CHOICES = [
        ('facebook', 'Facebook'),
        ('twitter', 'Twitter/X'),
        ('instagram', 'Instagram'),
        ('linkedin', 'LinkedIn'),
        ('youtube', 'YouTube'),
        ('tiktok', 'TikTok'),
        ('github', 'GitHub'),
        ('discord', 'Discord'),
        ('pinterest', 'Pinterest'),
        ('reddit', 'Reddit'),
        ('other', 'Other'),
    ]
    
    footer = ParentalKey(
        'Footer',
        related_name='social_links',
        on_delete=models.CASCADE
    )
    
    platform = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES,
        help_text="Social media platform"
    )
    url = models.URLField(help_text="Full URL to your social media profile")
    custom_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional custom label (defaults to platform name)"
    )
    
    panels = [
        FieldPanel('platform'),
        FieldPanel('url'),
        FieldPanel('custom_label'),
    ]
    
    api_fields = [
        APIField('platform'),
        APIField('url'),
        APIField('label'),
    ]
    
    @property
    def label(self):
        """Return custom label or platform name"""
        return self.custom_label if self.custom_label else self.get_platform_display()
    
    def __str__(self):
        return f"{self.label} - {self.url}"
    
    class Meta:
        verbose_name = "Social Media Link"
        verbose_name_plural = "Social Media Links"
