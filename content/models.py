from django.db import models

from wagtail.models import Page
from wagtail.fields import StreamField
from wagtail.admin.panels import FieldPanel
from wagtail.api import APIField
from wagtail import blocks
from wagtail.images.blocks import ImageChooserBlock
from wagtail.embeds.blocks import EmbedBlock


class FlexiblePage(Page):
    """A flexible page model that supports various HTML elements"""

    content = StreamField([
        ('heading', blocks.CharBlock(form_classname="title", icon="title")),
        ('paragraph', blocks.RichTextBlock(icon="pilcrow")),
        ('image', ImageChooserBlock(icon="image")),
        ('html', blocks.RawHTMLBlock(icon="code")),
        ('quote', blocks.BlockQuoteBlock(icon="openquote")),
        ('embed', EmbedBlock(icon="media")),
        ('list', blocks.ListBlock(blocks.CharBlock(), icon="list-ul")),
    ], use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('content'),
    ]

    api_fields = [
        APIField('content'),
    ]


class AdvancedFlexiblePage(Page):
    """An advanced flexible page with more complex block structures"""

    body = StreamField([
        ('heading', blocks.StructBlock([
            ('text', blocks.CharBlock(required=True)),
            ('level', blocks.ChoiceBlock(choices=[
                ('h1', 'Heading 1'),
                ('h2', 'Heading 2'),
                ('h3', 'Heading 3'),
                ('h4', 'Heading 4'),
                ('h5', 'Heading 5'),
                ('h6', 'Heading 6'),
            ], default='h2')),
        ], icon="title")),

        ('paragraph', blocks.RichTextBlock(icon="pilcrow")),

        ('image', blocks.StructBlock([
            ('image', ImageChooserBlock()),
            ('caption', blocks.CharBlock(required=False)),
            ('alt_text', blocks.CharBlock(required=False)),
        ], icon="image")),

        ('html', blocks.RawHTMLBlock(icon="code")),

        ('quote', blocks.StructBlock([
            ('quote', blocks.TextBlock()),
            ('author', blocks.CharBlock(required=False)),
        ], icon="openquote")),

        ('button', blocks.StructBlock([
            ('text', blocks.CharBlock()),
            ('url', blocks.URLBlock()),
            ('style', blocks.ChoiceBlock(choices=[
                ('primary', 'Primary'),
                ('secondary', 'Secondary'),
                ('outline', 'Outline'),
            ], default='primary')),
        ], icon="link")),

        ('embed', EmbedBlock(icon="media")),

        ('two_columns', blocks.StructBlock([
            ('left_column', blocks.StreamBlock([
                ('paragraph', blocks.RichTextBlock()),
                ('image', ImageChooserBlock()),
            ])),
            ('right_column', blocks.StreamBlock([
                ('paragraph', blocks.RichTextBlock()),
                ('image', ImageChooserBlock()),
            ])),
        ], icon="columns")),

        ('call_to_action', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('text', blocks.RichTextBlock()),
            ('button_text', blocks.CharBlock()),
            ('button_url', blocks.URLBlock()),
        ], icon="warning")),
    ], use_json_field=True, blank=True)

    content_panels = Page.content_panels + [
        FieldPanel('body'),
    ]

    api_fields = [
        APIField('body'),
    ]
