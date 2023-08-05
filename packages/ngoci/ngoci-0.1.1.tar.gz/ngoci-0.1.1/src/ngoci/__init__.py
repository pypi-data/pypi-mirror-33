# *- coding: utf-8 -*-
from ngoschema.schemas_loader import load_module_schemas
from ngoschema.transforms import transforms_module_loader
from ngoschema.jinja2 import templates_module_loader

load_module_schemas('ngoci')
templates_module_loader.register('ngoci')
transforms_module_loader.register('ngoci')

__author__ = "Cédric ROMAN"
__email__ = "roman@numengo.com"
__version__ = "__version__ = '0.1.1'"
