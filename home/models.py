from django.db import models

from wagtail.models import Page
from wagtail.fields import RichTextField, StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock


class HomePage(Page):
    """Flexible homepage with hero, about, stats, links, content boxes, projects, and news"""

    # Hero Section
    hero_title = models.CharField(max_length=255, blank=True)
    hero_subtitle = models.CharField(max_length=500, blank=True)
    hero_image = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    hero_cta_text = models.CharField(max_length=100, blank=True, help_text="Call to action button text")
    hero_cta_link = models.URLField(blank=True, help_text="Call to action button link")

    # About Section
    about_title = models.CharField(max_length=255, blank=True)
    about_content = RichTextField(blank=True)

    # Main Content - Flexible sections
    content_sections = StreamField([
        ('stats_section', blocks.StructBlock([
            ('title', blocks.CharBlock(required=False)),
            ('stats', blocks.ListBlock(
                blocks.StructBlock([
                    ('number', blocks.CharBlock(help_text="e.g., '500+', '$10M'")),
                    ('label', blocks.CharBlock(help_text="e.g., 'Users', 'Funding'")),
                    ('description', blocks.CharBlock(required=False)),
                    ('cta_text', blocks.CharBlock(required=False, help_text="Call to action text")),
                    ('cta_link', blocks.URLBlock(required=False, help_text="Call to action link")),
                ])
            )),
        ], icon='snippet')),

        ('links_section', blocks.StructBlock([
            ('title', blocks.CharBlock(required=False)),
            ('links', blocks.ListBlock(
                blocks.StructBlock([
                    ('title', blocks.CharBlock()),
                    ('url', blocks.URLBlock()),
                    ('description', blocks.TextBlock(required=False)),
                    ('icon', blocks.CharBlock(required=False, help_text="Icon class or emoji")),
                ])
            )),
        ], icon='link')),

        ('content_boxes', blocks.StructBlock([
            ('title', blocks.CharBlock(required=False)),
            ('boxes', blocks.ListBlock(
                blocks.StructBlock([
                    ('title', blocks.CharBlock()),
                    ('content', blocks.RichTextBlock()),
                    ('image', ImageChooserBlock(required=False)),
                    ('link_text', blocks.CharBlock(required=False)),
                    ('link_url', blocks.URLBlock(required=False)),
                ])
            )),
        ], icon='grid')),

        ('project_highlights', blocks.StructBlock([
            ('section_title', blocks.CharBlock(default="Project Highlights")),
            ('projects', blocks.ListBlock(
                blocks.StructBlock([
                    ('title', blocks.CharBlock()),
                    ('authors', blocks.CharBlock(required=False, help_text="Project authors")),
                    ('description', blocks.TextBlock(required=False)),
                    ('image', ImageChooserBlock(required=False)),
                    ('link_url', blocks.URLBlock(required=False)),
                    ('link_text', blocks.CharBlock(required=False)),
                    ('tags', blocks.ListBlock(blocks.CharBlock(required=False), required=False)),
                ])
            )),
        ], icon='doc-full')),

        ('news_section', blocks.StructBlock([
            ('section_title', blocks.CharBlock(default="Latest News")),
            ('news_items', blocks.ListBlock(
                blocks.StructBlock([
                    ('title', blocks.CharBlock()),
                    ('date', blocks.DateBlock(required=False)),
                    ('summary', blocks.RichTextBlock(required=False)),
                    ('image', ImageChooserBlock(required=False)),
                    ('link_url', blocks.URLBlock(required=False)),
                    ('link_text', blocks.CharBlock(required=False, help_text="Call to action text")),
                    ('category', blocks.CharBlock(required=False)),
                ])
            )),
        ], icon='date')),

        ('opportunities_section', blocks.StructBlock([
            ('section_title', blocks.CharBlock(default="Current Opportunities")),
            ('opportunities', blocks.ListBlock(
                blocks.StructBlock([
                    ('title', blocks.CharBlock()),
                    ('description', blocks.TextBlock()),
                    ('cta_text', blocks.CharBlock(help_text="Call to action button text")),
                    ('cta_link', blocks.URLBlock(help_text="Call to action button link")),
                    ('badge', blocks.CharBlock(required=False, help_text="e.g., 'New', 'Urgent', 'Featured'")),
                ])
            )),
        ], icon='pick')),

        ('rich_content_section', blocks.StructBlock([
            ('title', blocks.CharBlock(required=False)),
            ('content', blocks.StreamBlock([
                ('paragraph', blocks.RichTextBlock()),
                ('heading', blocks.CharBlock(form_classname='title')),
                ('image', blocks.StructBlock([
                    ('image', ImageChooserBlock()),
                    ('caption', blocks.CharBlock(required=False)),
                    ('alt_text', blocks.CharBlock(required=False)),
                ])),
                ('quote', blocks.BlockQuoteBlock()),
                ('list', blocks.ListBlock(blocks.CharBlock())),
                ('embed', blocks.URLBlock(help_text="URL to embed (YouTube, etc.)")),
            ])),
        ], icon='doc-full')),

        ('custom_html', blocks.RawHTMLBlock(icon='code')),

    ], use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('hero_title'),
        FieldPanel('hero_subtitle'),
        FieldPanel('hero_image'),
        FieldPanel('hero_cta_text'),
        FieldPanel('hero_cta_link'),
        FieldPanel('about_title'),
        FieldPanel('about_content'),
        FieldPanel('content_sections'),
    ]

    api_fields = [
        APIField('hero_title'),
        APIField('hero_subtitle'),
        APIField('hero_image'),
        APIField('hero_cta_text'),
        APIField('hero_cta_link'),
        APIField('about_title'),
        APIField('about_content'),
        APIField('content_sections'),
    ]

    max_count = 1  # Only one homepage


class HTMLPage(Page):
    body = RichTextField(blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    api_fields = [
        APIField('body'),
    ]
