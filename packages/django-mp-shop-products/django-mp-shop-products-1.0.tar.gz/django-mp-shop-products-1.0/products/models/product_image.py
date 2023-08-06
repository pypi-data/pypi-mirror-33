
from django.db import models
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _


DEFAULT_UPLOAD_TO = 'product_images'


class ImageProduct(models.ForeignKey):

    def __init__(
            self,
            to='products.Product',
            verbose_name=_("Product"),
            related_name='images',
            on_delete=models.CASCADE,
            *args, **kwargs):

        super(ImageProduct, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            *args, **kwargs)


class ImageFile(models.ImageField):

    def __init__(
            self,
            verbose_name=_("File"),
            upload_to=DEFAULT_UPLOAD_TO,
            max_length=255,
            *args, **kwargs):

        super(ImageFile, self).__init__(
            verbose_name=verbose_name,
            upload_to=upload_to,
            max_length=max_length,
            *args, **kwargs)


class ProductImageNotFoundError(IOError):
    pass


def get_product_image_class(upload_to=DEFAULT_UPLOAD_TO):

    class ProductImage(models.Model):

        product = ImageProduct()

        file = ImageFile(upload_to=upload_to)

        def get_preview(self, size):

            from sorl.thumbnail import get_thumbnail

            if not self.file:
                return None

            try:
                return get_thumbnail(self.file.file, size)
            except IOError:
                raise ProductImageNotFoundError()

        def get_preview_tag(self, width=100, empty_label='-----'):

            if not self.file:
                return empty_label

            try:
                url = self.get_preview(str(width)).url
            except ProductImageNotFoundError:
                return _('Image not found')

            return mark_safe(
                '<img src="{}" width: {}px; title="{}" />'.format(
                    url, width, self.file.url))

        @property
        def preview_tag(self):
            return self.get_preview_tag()

        preview_tag.fget.short_description = _('Preview')

        def __str__(self):
            return str(self.product)

        class Meta:
            abstract = True
            ordering = ['id']
            verbose_name = _('Product image')
            verbose_name_plural = _('Product images')

    return ProductImage


def get_ordered_product_image_class(upload_to=DEFAULT_UPLOAD_TO):

    from ordered_model.models import OrderedModelBase

    ProductImage = get_product_image_class(upload_to)

    class OrderedProductImage(OrderedModelBase, ProductImage):

        order = models.PositiveIntegerField(_('Ordering'), default=0)

        order_field_name = 'order'
        order_with_respect_to = 'product'

        class Meta(ProductImage.Meta):
            abstract = True
            ordering = ['order', 'id']

    return OrderedProductImage
