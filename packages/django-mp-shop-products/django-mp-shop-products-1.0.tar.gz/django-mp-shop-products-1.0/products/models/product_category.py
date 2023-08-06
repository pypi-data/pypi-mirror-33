
from django.db import models
from django.utils.translation import ugettext_lazy as _


class CategoryNameField(models.CharField):

    def __init__(
            self,
            verbose_name=_('Category name'),
            max_length=255,
            *args, **kwargs):

        super(CategoryNameField, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            *args, **kwargs)


class CategoryItemNameField(models.CharField):

    def __init__(
            self,
            verbose_name=_('Item name'),
            max_length=255,
            blank=True,
            *args, **kwargs):

        super(CategoryItemNameField, self).__init__(
            verbose_name=verbose_name,
            max_length=max_length,
            blank=blank,
            *args, **kwargs)


class CategoryDescriptionField(models.TextField):

    def __init__(
            self,
            verbose_name=_('Description'),
            blank=True,
            *args, **kwargs):

        super(CategoryDescriptionField, self).__init__(
            verbose_name=verbose_name,
            blank=blank,
            *args, **kwargs)


class CategoryLogoField(models.ImageField):

    def __init__(
            self,
            verbose_name=_('Logo'),
            upload_to='product_category_logos',
            blank=True,
            null=True,
            max_length=255,
            *args, **kwargs):

        super(CategoryLogoField, self).__init__(
            verbose_name=verbose_name,
            upload_to=upload_to,
            blank=blank,
            null=null,
            max_length=max_length,
            *args, **kwargs)


def get_mptt_parent_field(
        verbose_name=_('Parent category'),
        null=True,
        blank=True,
        related_name='children',
        db_index=True,
        on_delete=models.SET_NULL,
        *args, **kwargs):

    from mptt.models import TreeForeignKey

    return TreeForeignKey(
        'self',
        verbose_name=verbose_name,
        null=null,
        blank=blank,
        related_name=related_name,
        db_index=db_index,
        on_delete=on_delete,
        *args, **kwargs)
