# -*- coding: utf-8 -*-
""" 
author: Cedric ROMAN
email: roman@numengo.com
licence: GNU GPLv3 
"""
from __future__ import unicode_literals
from __future__ import print_function

import logging

logging.basicConfig(level=logging.WARNING)
#logging.getLogger('python_jsonschema_objects.classbuilder').setLevel(
#    logging.INFO)

from ngoci.project_loader import get_project_loader
from ngoci.project import Cookiecutter

def test_toxEnv():
    pl = get_project_loader()
    pl.load_from_file(r'D:\CODES\ngoci.ngocc', fromObjectClass=Cookiecutter)
    p = pl.get('NgoCI')
    p.toxEnv
    p.toxEnv.config.toxworkdir
    p.toxEnv.config.envlist
    p.toxEnv.get_env('py27').update_from_pyexe()
    print(p.toxEnv.get_env('py27').packages)

if __name__ == "__main__":
    test_toxEnv()
