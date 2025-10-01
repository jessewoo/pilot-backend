from wagtail.api.v2.views import PagesAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from wagtail.models import Page


api_router = WagtailAPIRouter('wagtailapi')
api_router.register_endpoint('pages', PagesAPIViewSet)


@api_view(['GET'])
def page_by_slug(request):
    """
    API endpoint to get a page by slug with all fields.
    Usage: /api/v2/page-by-slug/?slug=about-us
    """
    slug = request.GET.get('slug')

    if not slug:
        return Response(
            {'error': 'slug parameter is required'},
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        # Get the page by slug
        page = Page.objects.filter(slug=slug).live().first()

        if not page:
            return Response(
                {'error': f'Page with slug "{slug}" not found'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get the specific page type instance
        page = page.specific

        # Build response with all fields
        data = {
            'id': page.id,
            'title': page.title,
            'slug': page.slug,
            'url_path': page.url_path,
            'seo_title': page.seo_title,
            'search_description': page.search_description,
            'live': page.live,
            'has_unpublished_changes': page.has_unpublished_changes,
            'first_published_at': page.first_published_at,
            'last_published_at': page.last_published_at,
        }

        # Add custom fields if they exist
        if hasattr(page, 'body'):
            data['body'] = str(page.body)

        # Add any other custom fields from the specific page model
        for field in page._meta.get_fields():
            field_name = field.name
            # Skip some fields to avoid recursion and redundant data
            if field_name not in data and not field_name.startswith('_') and field_name not in ['page_ptr', 'content_type']:
                try:
                    field_value = getattr(page, field_name, None)
                    # Convert to string or serializable format
                    if field_value is not None and not callable(field_value):
                        data[field_name] = str(field_value) if not isinstance(field_value, (str, int, bool, float, list, dict)) else field_value
                except Exception:
                    pass

        return Response(data)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
