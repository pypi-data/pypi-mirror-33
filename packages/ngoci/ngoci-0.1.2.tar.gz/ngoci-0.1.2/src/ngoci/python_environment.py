# *- coding: utf-8 -*-
"""
Class for code Environment

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import gettext
import pathlib
import py
import py.path
import tox
import subprocess

from builtins import object
from builtins import str

from future.utils import with_metaclass

from ngofile.list_files import list_files
from ngoschema.str_utils import split_string
from ngoschema.schema_metaclass import SchemaMetaclass
from ngoschema.classbuilder import ProtocolBase
from ngoschema.decorators import assert_prop
from ngoschema.config import ConfigLoader

_ = gettext.gettext


class PythonEnvironment(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaUri = r"http://numengo.org/ngoci/python_environment"

    def set_path(self, value):
        p = pathlib.Path(str(value))
        if p.name.split(".")[0] in ["python", "pypy"]:
            self._pyexe = p.name
        if not p.is_dir():
            p = p.parent
        self.set_prop("path", p)

    def update_from_path(self):
        p = self.path
        self._pyexe = next(
            list_files(
                p,
                ["python.exe", "python", "pypy", "pypy.exe"],
                ["libs", "Lib", "tcl", "include"],
                recursive=True,
            ),
            None,
        )
        if not self._pyexe:
            raise ValueError(_("No python interpreter found in %s" % p))

        self._pipexe = next(
            list_files(
                p, ["pip.exe", "pip"], ["libs", "Lib", "tcl", "include"],
                recursive=True),
            None,
        )

        self._activate_script = next(
            list_files(
                p,
                ["activate_this.py"],
                ["libs", "Lib", "tcl", "include"],
                recursive=True,
            ),
            None,
        )

    def update_from_pyexe(self):
        """
        Retrieve version/archi from python exectuable.
        """
        if not hasattr(self, "_pyexe"):
            self.update_from_path()
        pyexe = py.path.local(str(self._pyexe))
        out = pyexe.sysexec(
            "-c",
            "import sys; "
            "print(list(sys.version_info)); "
            "import platform;"
            "print(platform.architecture()[0]);"
            "print(sys.version);",
        )
        lines = out.splitlines()
        ver = eval(lines.pop(0))
        self.version = "%i.%i.%i" % (ver[0], ver[1], ver[2])
        self.archi = lines.pop(0)
        self.versionLong = "\n".join(lines)

        if self._pipexe:
            pipexe = py.path.local(str(self._pipexe))
            out = pipexe.sysexec("freeze")
            self.packages = out.splitlines()

    @property
    @assert_prop("_pyexe")
    def python_exe(self):
        return self._pyexe

    @assert_prop("_pyexe")
    def python(self, *args):
        subprocess.call([str(self._pyexe)] + args)

    @assert_prop("_activate_script")
    def activate(self):
        self.python(str(self._activate_script))

    @assert_prop("_pipexe")
    def pip(self, command, *args):
        """
        Run a pip command on environment.
        """
        cmds = [str(self._pipexe), command]
        cmds += [str(a) for a in args]
        subprocess.call(cmds)

    @assert_prop("_pipexe")
    def install(self, *args):
        self.pip("install", *args)


class ToxEnvironment(object):
    def __init__(self, configFile):
        self.pythonEnvs = {}
        self.configFile = pathlib.Path(configFile).resolve()
        if not self.configFile.exists():
            raise AttributeError(_("%s does not exist." % configFile))
        self._config = tox.config.parseconfig(["-c", str(self.configFile)])
        self._envs = {}

    @property
    def config(self):
        return self._config

    def get_env(self, name):
        if name in self._envs:
            return self._envs[name]
        if name not in self.config.envlist:
            raise AttributeError(
                _("%s not in envlist %s." % (name, self.config.envlist)))
        envpath = str(self.config.toxworkdir.join(name))
        env = PythonEnvironment(path=envpath)
        env.update_from_path()
        self._envs[name] = env
        return env
