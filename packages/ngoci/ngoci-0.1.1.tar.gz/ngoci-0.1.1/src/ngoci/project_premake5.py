# -*- coding: utf-8 -*-
""" 
create premake template for project

author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3  
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import unicode_literals

from ngoschema.jinja2 import Jinja2Serializer
from .project_loader import get_project_loader
from ngomf.protected_regions import get_protected_regions_from_file


def create_project_premake5(project):
    fp = project.repoDir.joinpath('premake5.lua')
    user_code = get_protected_regions_from_file(fp)
    deps = [get_project_loader().get(d) for d in project.deps]
    Jinja2Serializer('ngoci/premake5.lua').dump(
        {
            "project": project,
            "deps": deps,
            "user_code": user_code
        },
        fp,
        overwrite=True)
    return fp
