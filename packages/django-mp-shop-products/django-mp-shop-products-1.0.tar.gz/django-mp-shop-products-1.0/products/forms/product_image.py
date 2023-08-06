
from django.apps import apps
from django.utils.translation import ugettext_lazy as _


def get_multi_image_field(
        label=_('Images'),
        max_num=100,
        min_num=1,
        required=False):

    from multiupload.fields import MultiFileField

    return MultiFileField(
        label=label,
        max_num=max_num,
        min_num=min_num,
        required=required)


def get_suit_sortable_tabular_inline():

    from suit.sortables import SortableTabularInline

    class ImageInline(SortableTabularInline):

        fields = ['preview_tag']
        readonly_fields = ['preview_tag']
        model = apps.get_model('products', 'ProductImage')
        extra = 0
        max_num = 0

    return ImageInline
