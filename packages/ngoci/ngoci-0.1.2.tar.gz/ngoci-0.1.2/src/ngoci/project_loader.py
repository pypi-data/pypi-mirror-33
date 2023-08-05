# *- coding: utf-8 -*-
"""
Class for code Projects management

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import pathlib
import py
import py.path

from builtins import str
from future.utils import text_to_native_str as native_str
from future.utils import with_metaclass

from ngoschema.schema_metaclass import SchemaMetaclass
from ngoschema.classbuilder import ProtocolBase
from ngoschema.transforms import ObjectTransform
from ngoschema.object_loader import ObjectLoader
from ngoschema.deserializers import YamlDeserializer
from ngoschema.deserializers import JsonDeserializer

_ = gettext.gettext

_default_project_loader = None


def get_project_loader():
    """
    Return the default project loader
    """
    global _default_project_loader
    if _default_project_loader is None:
        _default_project_loader = ProjectLoader()
    return _default_project_loader


class ProjectLoader(with_metaclass(SchemaMetaclass, ObjectLoader)):
    deserializers = [JsonDeserializer, YamlDeserializer]
    primaryKey = "name"

    def __init__(self):
        ObjectLoader.__init__(self, objectClass="ngoci.project.Project")
        cc2prj_fp = pathlib.Path(__file__).with_name("transforms").joinpath(
            "cookiecutter2project.mtm")
        if cc2prj_fp.exists():
            cc2prj = JsonDeserializer().load(
                cc2prj_fp, objectClass=ObjectTransform)
            self.add_transformation(cc2prj)

    def _get_objects_from_data(self, data, objectClass, **opts):
        """
        Returns a list of objects found in data
        Can be overrided by subclasses to add specific treatments
        """
        from .project import Cookiecutter, Project
        if issubclass(objectClass, Cookiecutter):
            if 'default_context' in data:
                return [objectClass(**(data['default_context']))]
        if issubclass(objectClass, Project):
            props = set(objectClass.__prop_names__)
            if set(data.keys()).intersection(props):
                return [objectClass(**data)]
            else:
                return [
                    objectClass(**v) for v in data.values()
                    if set(v.keys()).intersection(props)
                ]

    def load_from_file(self, fp, **opts):
        """
        Load objects from a file

        :type fp: path
        """
        objs = ObjectLoader.load_from_file(self, fp, **opts)
        for o in objs:
            if fp.with_name(str(o.repoName)).exists():
                o.repoDir = fp.with_name(str(o.repoName))
        return objs

    def sort(self):
        # adapted from https://stackoverflow.com/questions/11557241/python-sorting-a-dependency-list/11564769#11564769
        items = [(prj, set([str(d) for d in prj.deps]))
                 for prj in self.objects]
        provided = set()
        while items:
            remaining_items = []
            emitted = False

            for item, dependencies in items:
                if dependencies.issubset(provided):
                    yield item
                    provided.add(str(item.name))
                    emitted = True
                else:
                    remaining_items.append((item, dependencies))

            if not emitted:
                raise Exception()

            items = remaining_items
