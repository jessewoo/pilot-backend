from wagtail.api.v2.views import PagesAPIViewSet, BaseAPIViewSet
from wagtail.api.v2.router import WagtailAPIRouter
from wagtail.api.v2.serializers import BaseSerializer, Field
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status, serializers
from wagtail.models import Page
from wagtail.images.api.fields import ImageRenditionField
from navigation.models import NavigationMenu, MenuItem, SubMenuItem


class SubMenuItemSerializer(serializers.ModelSerializer):
    link = serializers.CharField(read_only=True)

    class Meta:
        model = SubMenuItem
        fields = ['title', 'link', 'link_url', 'description', 'open_in_new_tab']


class MenuItemSerializer(serializers.ModelSerializer):
    link = serializers.CharField(read_only=True)
    sub_items = SubMenuItemSerializer(many=True, read_only=True)

    class Meta:
        model = MenuItem
        fields = ['title', 'link', 'link_url', 'open_in_new_tab', 'sub_items']


class NavigationMenuSerializer(BaseSerializer):
    menu_items = MenuItemSerializer(many=True, read_only=True)
    link = serializers.CharField(read_only=True)

    class Meta:
        model = NavigationMenu
        fields = ['id', 'title', 'slug', 'link', 'link_url', 'display_order', 'menu_items']


class NavigationMenuAPIViewSet(BaseAPIViewSet):
    model = NavigationMenu
    serializer_class = NavigationMenuSerializer
    body_fields = ['title', 'slug', 'link', 'link_url', 'display_order', 'menu_items']
    listing_default_fields = ['id', 'title', 'slug', 'link', 'display_order', 'menu_items']

    def get_queryset(self):
        return NavigationMenu.objects.all().prefetch_related('menu_items__sub_items')


class StreamFieldSerializer(Field):
    """Custom serializer for StreamField that returns JSON instead of HTML"""
    def to_representation(self, value):
        # Convert StreamField to list of dicts
        result = []
        for block in value:
            result.append({
                'type': block.block_type,
                'value': self._serialize_block_value(block.value),
                'id': str(block.id) if hasattr(block, 'id') else None
            })
        return result

    def _serialize_block_value(self, value):
        """Serialize a block's value"""
        # Handle StructValue
        if hasattr(value, 'items'):
            return self._serialize_struct_block(value)
        # Handle basic types
        elif isinstance(value, (str, int, float, bool, type(None))):
            return value
        # Handle lists
        elif isinstance(value, (list, tuple)):
            return [self._serialize_block_value(item) for item in value]
        # Default
        else:
            return self._serialize_value(value)

    def _serialize_struct_block(self, struct_value):
        """Recursively serialize StructBlock values"""
        result = {}
        for key, val in struct_value.items():
            result[key] = self._serialize_value(val)
        return result

    def _serialize_value(self, value):
        """Serialize individual values"""
        from wagtail.rich_text import RichText
        from wagtail.images.models import Image
        from wagtail.blocks.stream_block import StreamValue
        from wagtail.blocks.list_block import ListValue
        from datetime import date, datetime

        # Handle None
        if value is None:
            return None

        # Handle basic types first
        if isinstance(value, (str, int, float, bool)):
            return value

        # Handle ListValue (from ListBlock) - must come before list/tuple check
        if isinstance(value, ListValue):
            return [self._serialize_value(item) for item in value]

        # Handle StructValue (nested blocks) - check for items() method
        if hasattr(value, 'items') and callable(value.items):
            return self._serialize_struct_block(value)

        # Handle StreamValue (nested StreamField)
        if isinstance(value, StreamValue):
            return self.to_representation(value)

        # Handle regular lists/tuples
        if isinstance(value, (list, tuple)):
            return [self._serialize_value(item) for item in value]

        # Handle RichText
        if isinstance(value, RichText):
            return str(value)

        # Handle Images
        if isinstance(value, Image):
            return {
                'id': value.id,
                'title': value.title,
                'url': value.file.url,
                'width': value.width,
                'height': value.height,
            }

        # Handle dates
        if isinstance(value, (date, datetime)):
            return value.isoformat()

        # Default: convert to string
        return str(value)


class CustomPagesAPIViewSet(PagesAPIViewSet):
    """Custom Pages API that properly serializes StreamFields"""

    def get_serializer_class(self):
        # Get the default serializer class
        serializer_class = super().get_serializer_class()

        # Override StreamField serialization
        original_get_fields = serializer_class.get_fields

        def get_fields(self):
            fields = original_get_fields(self)
            # Replace StreamField serialization
            for field_name in list(fields.keys()):
                if hasattr(self.instance, field_name):
                    field_value = getattr(self.instance, field_name)
                    if hasattr(field_value, 'stream_block'):  # It's a StreamField
                        fields[field_name] = StreamFieldSerializer(source=field_name)
            return fields

        serializer_class.get_fields = get_fields
        return serializer_class


api_router = WagtailAPIRouter('wagtailapi')
api_router.register_endpoint('pages', CustomPagesAPIViewSet)
api_router.register_endpoint('navigation_menus', NavigationMenuAPIViewSet)


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

        # Helper function to serialize field values
        def serialize_field_value(field_value):
            from wagtail.rich_text import RichText
            from wagtail.images.models import Image
            from datetime import date, datetime

            # Handle StreamField
            if hasattr(field_value, 'stream_block'):
                serializer = StreamFieldSerializer()
                return serializer.to_representation(field_value)

            # Handle RichText
            if isinstance(field_value, RichText):
                return str(field_value)

            # Handle Images
            if isinstance(field_value, Image):
                return {
                    'id': field_value.id,
                    'title': field_value.title,
                    'url': field_value.file.url,
                    'width': field_value.width,
                    'height': field_value.height,
                }

            # Handle dates
            if isinstance(field_value, (date, datetime)):
                return field_value.isoformat()

            return field_value

        # Add any other custom fields from the specific page model
        for field in page._meta.get_fields():
            field_name = field.name
            # Skip some fields to avoid recursion and redundant data
            if field_name not in data and not field_name.startswith('_') and field_name not in ['page_ptr', 'content_type']:
                try:
                    field_value = getattr(page, field_name, None)
                    # Convert to serializable format
                    if field_value is not None and not callable(field_value):
                        serialized_value = serialize_field_value(field_value)
                        if not isinstance(serialized_value, (str, int, bool, float, list, dict, type(None))):
                            serialized_value = str(serialized_value)
                        data[field_name] = serialized_value
                except Exception:
                    pass

        return Response(data)

    except Exception as e:
        return Response(
            {'error': str(e)},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
