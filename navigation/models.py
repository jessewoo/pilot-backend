from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel, PageChooserPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet


@register_snippet
class NavigationMenu(ClusterableModel):
    """Main navigation menu that can contain multiple menu items"""

    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)

    # Optional link for the menu itself
    link_page = models.ForeignKey(
        'wagtailcore.Page',
        null=True,
        blank=True,
        related_name='+',
        on_delete=models.SET_NULL,
        help_text="Optional: Link this menu directly to a page"
    )
    link_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Optional: Or link to a URL (can be relative like /about or full URL)"
    )

    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first in the list"
    )

    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('display_order'),
        InlinePanel('menu_items', label="Menu Items (optional - leave empty for simple link)"),
    ]

    @property
    def link(self):
        """Return the appropriate link (page or URL)"""
        if self.link_page:
            return self.link_page.url
        return self.link_url

    def __str__(self):
        return self.title

    class Meta:
        verbose_name = "Navigation Menu"
        verbose_name_plural = "Navigation Menus"
        ordering = ['display_order', 'title']


class MenuItem(ClusterableModel, Orderable):
    """A single menu item that can have sub-items"""

    menu = ParentalKey(
        'NavigationMenu',
        related_name='menu_items',
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
    link_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Or link to a URL (can be relative like /about or full URL)"
    )
    open_in_new_tab = models.BooleanField(default=False)

    panels = [
        FieldPanel('title'),
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('open_in_new_tab'),
        InlinePanel('sub_items', label="Sub Menu Items", heading="Sub Menu Items"),
    ]

    class Meta(Orderable.Meta):
        ordering = ['sort_order']
    
    api_fields = [
        APIField('title'),
        APIField('link_page'),
        APIField('link_url'),
        APIField('open_in_new_tab'),
        APIField('sub_items'),
    ]
    
    @property
    def link(self):
        """Return the appropriate link (page or URL)"""
        if self.link_page:
            return self.link_page.url
        return self.link_url
    
    def __str__(self):
        return self.title


class SubMenuItem(Orderable):
    """Sub-navigation item (nested under MenuItem)"""
    
    parent_item = ParentalKey(
        'MenuItem',
        related_name='sub_items',
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
    link_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="Or link to a URL (can be relative like /about or full URL)"
    )
    open_in_new_tab = models.BooleanField(default=False)
    description = models.CharField(
        max_length=255,
        blank=True,
        help_text="Optional short description"
    )
    
    panels = [
        FieldPanel('title'),
        PageChooserPanel('link_page'),
        FieldPanel('link_url'),
        FieldPanel('description'),
        FieldPanel('open_in_new_tab'),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('link_page'),
        APIField('link_url'),
        APIField('description'),
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


# Alternative approach: Mega Menu with StreamField for more flexibility

@register_snippet
class MegaMenu(ClusterableModel):
    """Flexible mega menu using StreamField"""
    
    from wagtail.fields import StreamField
    from wagtail import blocks
    
    title = models.CharField(max_length=100)
    slug = models.SlugField(unique=True, max_length=100)
    
    menu_items = StreamField([
        ('menu_item', blocks.StructBlock([
            ('title', blocks.CharBlock()),
            ('link_page', blocks.PageChooserBlock(required=False)),
            ('link_url', blocks.URLBlock(required=False)),
            ('open_in_new_tab', blocks.BooleanBlock(required=False, default=False)),
            ('sub_items', blocks.ListBlock(
                blocks.StructBlock([
                    ('title', blocks.CharBlock()),
                    ('link_page', blocks.PageChooserBlock(required=False)),
                    ('link_url', blocks.URLBlock(required=False)),
                    ('description', blocks.CharBlock(required=False, max_length=255)),
                    ('open_in_new_tab', blocks.BooleanBlock(required=False, default=False)),
                ])
            )),
        ])),
    ], use_json_field=True, blank=True)
    
    panels = [
        FieldPanel('title'),
        FieldPanel('slug'),
        FieldPanel('menu_items'),
    ]
    
    api_fields = [
        APIField('title'),
        APIField('slug'),
        APIField('menu_items'),
    ]
    
    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "Mega Menu"
        verbose_name_plural = "Mega Menus"
