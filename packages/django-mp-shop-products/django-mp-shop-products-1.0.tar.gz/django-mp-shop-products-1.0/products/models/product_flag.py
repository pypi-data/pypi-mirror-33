
from django.db import models
from django.utils.translation import ugettext_lazy as _


class ProductFlagsField(models.ManyToManyField):

    def __init__(
            self,
            to='products.ProductFlag',
            verbose_name=_('Flags'),
            related_name='products',
            blank=True,
            *args, **kwargs):

        super(ProductFlagsField, self).__init__(
            to,
            verbose_name=verbose_name,
            related_name=related_name,
            blank=blank,
            *args, **kwargs)


class AbstractProductFlag(models.Model):

    title = models.CharField(_('Title'), max_length=255, blank=True)

    def __str__(self):
        return self.title

    def get_random_products(self, count=6):
        return self.products.visible().order_by('?')[:count]

    class Meta:
        abstract = True
        verbose_name = _('Product flag')
        verbose_name_plural = _('Product flags')
