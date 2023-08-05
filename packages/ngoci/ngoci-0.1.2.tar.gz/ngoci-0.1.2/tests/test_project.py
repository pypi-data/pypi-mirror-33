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


def test_Project_create_premake5():
    pl = get_project_loader()
    pl.load_from_file(r'D:\CODES\projects.ngoprj')
    prj = pl.get("NgoGeo")
    create_project_premake5(prj)

def test_Project_docker():
    pl = get_project_loader()
    pl.load_from_file(r'D:\CODES\projects.ngoprj')
    prj = pl.get("NgoGeo")
    wd = prj.repoDir.relative_to(prj.repoDir.anchor).as_posix()
    prj.docker('premake5 gmake', working_dir='/app/%s' % wd)


def test_Project_docker_build():
    pl = get_project_loader()
    pl.load_from_file(r'D:\CODES\projects.ngoprj')
    prj = pl.get("NgoErr")
    prj.docker_build5()


def test_ProjectLoader():
    pl = get_project_loader()
    pl.load_from_file(r'D:\CODES\ngoci.ngocc', fromObjectClass=Cookiecutter)
    pl.load_from_file(r'D:\CODES\projects.ngoprj')
    prj = pl.pick_first(name="NgoGeo")
    for prj in pl:
        if prj.setup_py is not None:
            prj.update_from_setup()
        else:
            #prj.premake()


def test_sort_projects():
    pl = get_project_loader()
    pl.load_from_file(r'D:\CODES\projects.ngoprj')
    prjs = [str(p.name) for p in pl.sort()]
    assert prjs


if __name__ == "__main__":
    #test_Project_create_premake5()
    #test_Project_docker()
    #test_Project_docker_build()
    #test_ProjectLoader()
    test_sort_projects()
