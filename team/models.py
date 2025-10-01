from django.db import models
from modelcluster.fields import ParentalKey
from modelcluster.models import ClusterableModel

from wagtail.models import Orderable
from wagtail.admin.panels import FieldPanel, InlinePanel, MultiFieldPanel
from wagtail.api import APIField
from wagtail.snippets.models import register_snippet
from wagtail.images.models import Image
from wagtail.fields import RichTextField


@register_snippet
class Role(models.Model):
    """Job roles/positions for team members"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g., 'Software Engineer', 'Marketing Manager', 'CEO'"
    )
    description = models.TextField(
        blank=True,
        help_text="Brief description of this role"
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
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['display_order', 'name']
        verbose_name = "Role"
        verbose_name_plural = "Roles"


@register_snippet
class Department(models.Model):
    """Departments or teams within the organization"""
    
    name = models.CharField(
        max_length=100,
        unique=True,
        help_text="e.g., 'Engineering', 'Marketing', 'Sales'"
    )
    description = models.TextField(blank=True)
    
    panels = [
        FieldPanel('name'),
        FieldPanel('description'),
    ]
    
    api_fields = [
        APIField('name'),
        APIField('description'),
    ]
    
    def __str__(self):
        return self.name
    
    class Meta:
        ordering = ['name']
        verbose_name = "Department"
        verbose_name_plural = "Departments"


@register_snippet
class TeamMember(ClusterableModel):
    """Individual team member/employee profile"""
    
    # Basic Information
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    full_name = models.CharField(
        max_length=255,
        blank=True,
        help_text="Leave blank to auto-generate from first and last name"
    )
    
    # Profile
    photo = models.ForeignKey(
        'wagtailimages.Image',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='+'
    )
    bio = RichTextField(
        blank=True,
        help_text="Team member biography"
    )
    short_bio = models.CharField(
        max_length=255,
        blank=True,
        help_text="Short bio for card displays"
    )
    
    # Position/Role
    role = models.ForeignKey(
        'Role',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_members'
    )
    custom_title = models.CharField(
        max_length=200,
        blank=True,
        help_text="Custom job title (overrides role if provided)"
    )
    department = models.ForeignKey(
        'Department',
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='team_members'
    )
    
    # Contact Information
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=50, blank=True)
    
    # Author Information
    is_author = models.BooleanField(
        default=False,
        help_text="Can this person author blog posts or articles?"
    )
    author_slug = models.SlugField(
        max_length=100,
        blank=True,
        help_text="URL-friendly name for author pages"
    )
    
    # Display Settings
    is_featured = models.BooleanField(
        default=False,
        help_text="Feature this member on team pages"
    )
    is_active = models.BooleanField(
        default=True,
        help_text="Is this person currently with the organization?"
    )
    display_order = models.IntegerField(
        default=0,
        help_text="Lower numbers appear first"
    )
    
    # Dates
    joined_date = models.DateField(
        null=True,
        blank=True,
        help_text="When they joined the organization"
    )
    
    panels = [
        MultiFieldPanel([
            FieldPanel('first_name'),
            FieldPanel('last_name'),
            FieldPanel('full_name'),
            FieldPanel('photo'),
        ], heading="Basic Information"),
        
        MultiFieldPanel([
            FieldPanel('bio'),
            FieldPanel('short_bio'),
        ], heading="Biography"),
        
        MultiFieldPanel([
            FieldPanel('role'),
            FieldPanel('custom_title'),
            FieldPanel('department'),
        ], heading="Position"),
        
        MultiFieldPanel([
            FieldPanel('email'),
            FieldPanel('phone'),
        ], heading="Contact Information"),
        
        MultiFieldPanel([
            FieldPanel('is_author'),
            FieldPanel('author_slug'),
        ], heading="Author Settings"),
        
        MultiFieldPanel([
            FieldPanel('is_featured'),
            FieldPanel('is_active'),
            FieldPanel('display_order'),
            FieldPanel('joined_date'),
        ], heading="Display & Status"),
        
        InlinePanel('social_links', label="Social Media Links"),
        InlinePanel('expertise_areas', label="Expertise/Skills"),
    ]
    
    api_fields = [
        APIField('first_name'),
        APIField('last_name'),
        APIField('full_name'),
        APIField('photo'),
        APIField('bio'),
        APIField('short_bio'),
        APIField('title'),
        APIField('role'),
        APIField('department'),
        APIField('email'),
        APIField('phone'),
        APIField('is_author'),
        APIField('author_slug'),
        APIField('is_featured'),
        APIField('is_active'),
        APIField('joined_date'),
        APIField('social_links'),
        APIField('expertise_areas'),
    ]
    
    def save(self, *args, **kwargs):
        # Auto-generate full_name if not provided
        if not self.full_name:
            self.full_name = f"{self.first_name} {self.last_name}".strip()
        
        # Auto-generate author_slug if is_author and slug not provided
        if self.is_author and not self.author_slug:
            from django.utils.text import slugify
            self.author_slug = slugify(self.full_name)
        
        super().save(*args, **kwargs)
    
    @property
    def title(self):
        """Return custom title or role name"""
        if self.custom_title:
            return self.custom_title
        if self.role:
            return self.role.name
        return ""
    
    def __str__(self):
        return self.full_name or f"{self.first_name} {self.last_name}"
    
    class Meta:
        ordering = ['display_order', 'last_name', 'first_name']
        verbose_name = "Team Member"
        verbose_name_plural = "Team Members"


class TeamMemberSocialLink(Orderable):
    """Social media links for team members"""
    
    PLATFORM_CHOICES = [
        ('linkedin', 'LinkedIn'),
        ('twitter', 'Twitter/X'),
        ('github', 'GitHub'),
        ('dribbble', 'Dribbble'),
        ('behance', 'Behance'),
        ('instagram', 'Instagram'),
        ('facebook', 'Facebook'),
        ('youtube', 'YouTube'),
        ('website', 'Personal Website'),
        ('other', 'Other'),
    ]
    
    team_member = ParentalKey(
        'TeamMember',
        related_name='social_links',
        on_delete=models.CASCADE
    )
    
    platform = models.CharField(
        max_length=50,
        choices=PLATFORM_CHOICES
    )
    url = models.URLField()
    custom_label = models.CharField(
        max_length=100,
        blank=True,
        help_text="Optional custom label"
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
        return self.custom_label if self.custom_label else self.get_platform_display()
    
    def __str__(self):
        return f"{self.label} - {self.url}"


class ExpertiseArea(Orderable):
    """Skills or areas of expertise for team members"""
    
    team_member = ParentalKey(
        'TeamMember',
        related_name='expertise_areas',
        on_delete=models.CASCADE
    )
    
    name = models.CharField(
        max_length=100,
        help_text="e.g., 'Python', 'Project Management', 'UX Design'"
    )
    proficiency_level = models.CharField(
        max_length=50,
        choices=[
            ('beginner', 'Beginner'),
            ('intermediate', 'Intermediate'),
            ('advanced', 'Advanced'),
            ('expert', 'Expert'),
        ],
        blank=True
    )
    
    panels = [
        FieldPanel('name'),
        FieldPanel('proficiency_level'),
    ]
    
    api_fields = [
        APIField('name'),
        APIField('proficiency_level'),
    ]
    
    def __str__(self):
        if self.proficiency_level:
            return f"{self.name} ({self.get_proficiency_level_display()})"
        return self.name
