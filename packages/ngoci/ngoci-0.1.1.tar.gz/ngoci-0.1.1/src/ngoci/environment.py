# *- coding: utf-8 -*-
"""
Class for environment definition

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

from future.utils import text_to_native_str as native_str
from future.utils import with_metaclass

from ngoschema.schema_metaclass import SchemaMetaclass
from ngoschema.classbuilder import ProtocolBase
from ngoschema.config import ConfigLoader
from ngoschema.config import search_app_config_files

# default jinja2 environment instance
_default_environment = None


def get_environment():
    """
    Return the default Environment loaded from config file
    """
    global _default_environment
    if _default_environment is None:
        _default_environment = Environment()
        _default_environment.load_from_config('NgoCI', 'Numengo')
    return _default_environment


class Environment(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaUri = r"http://numengo.org/ngoci/environment"

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, *args, **kwargs)
        #if 'envVars' not in kwargs:
        #    self.envVars = os.environ.copy()

    def load_from_config(self, app_name=None, app_author=None):
        cfg = ConfigLoader(*(search_app_config_files(app_name, app_author)))
        self.envVars = cfg.section('Environment')
