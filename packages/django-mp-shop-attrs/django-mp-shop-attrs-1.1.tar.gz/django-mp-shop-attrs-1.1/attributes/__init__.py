
from django.apps import AppConfig
from django.utils.translation import ugettext_lazy as _


__version__ = '1.1'


class AttributesAppConfig(AppConfig):

    name = 'attributes'
    verbose_name = _('Attributes')

    product_model = 'products.Product'
    product_category_model = 'products.ProductCategory'


default_app_config = 'attributes.AttributesAppConfig'
