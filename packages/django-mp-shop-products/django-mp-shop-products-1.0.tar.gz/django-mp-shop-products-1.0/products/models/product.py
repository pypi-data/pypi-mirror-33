
from django.db import models
from django.utils.translation import ugettext_lazy as _

from products import constants


class ProductAvailabilityField(models.PositiveIntegerField):

    def __init__(
            self,
            verbose_name=_('Availability'),
            choices=constants.AVAILABILITY_CHOICES,
            default=constants.AVAILABILITY_IN_STOCK,
            *args, **kwargs):

        super(ProductAvailabilityField, self).__init__(
            verbose_name=verbose_name,
            choices=choices,
            default=default,
            *args, **kwargs)


class ProductVisibilityField(models.BooleanField):

    def __init__(
            self,
            verbose_name=_('Is visible'),
            default=True,
            *args, **kwargs):

        super(ProductVisibilityField, self).__init__(
            verbose_name=verbose_name,
            default=default,
            *args, **kwargs)


class ProductCategoryField(models.ForeignKey):

    def __init__(
            self,
            to='products.ProductCategory',
            verbose_name=_('Category'),
            related_name='products',
            on_delete=models.CASCADE,
            *args, **kwargs):

        super(ProductCategoryField, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            on_delete=on_delete,
            *args, **kwargs)


class ProductNameField(models.CharField):

    def __init__(
            self,
            verbose_name=_('Product name'),
            max_length=255,
            blank=True,
            *args, **kwargs):

        super(ProductNameField, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class ProductCodeField(models.CharField):

    def __init__(
            self,
            verbose_name=_('Code'),
            max_length=255,
            blank=True,
            *args, **kwargs):

        super(ProductCodeField, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)

    @property
    def printable(self):
        return self or _('Not specified')


class ProductPriceField(models.FloatField):

    def __init__(
            self,
            verbose_name=_('Price'),
            *args, **kwargs):

        super(ProductPriceField, self).__init__(
            verbose_name=verbose_name,
            *args, **kwargs)


class ProductOldPriceField(models.FloatField):

    def __init__(
            self,
            verbose_name=_('Old price'),
            blank=True,
            null=True,
            *args, **kwargs):

        super(ProductOldPriceField, self).__init__(
            verbose_name=verbose_name,
            blank=blank,
            null=null,
            *args, **kwargs)


class ProductDescriptionField(models.TextField):

    def __init__(
            self,
            verbose_name=_('Description'),
            blank=True,
            *args, **kwargs):

        super(ProductDescriptionField, self).__init__(
            verbose_name=verbose_name,
            blank=blank,
            *args, **kwargs)


class ProductLogoField(models.ImageField):

    def __init__(
            self,
            verbose_name=_('Logo'),
            upload_to='product_logos',
            blank=True,
            null=True,
            max_length=255,
            editable=False,
            *args, **kwargs):

        super(ProductLogoField, self).__init__(
            verbose_name=verbose_name,
            upload_to=upload_to,
            blank=blank,
            null=null,
            max_length=max_length,
            editable=editable,
            *args, **kwargs)
