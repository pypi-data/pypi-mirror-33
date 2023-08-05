# *- coding: utf-8 -*-
"""
Project definition and main actions

author: Cédric ROMAN (roman@numengo.com)
licence: GPL3
"""
from __future__ import absolute_import
from __future__ import unicode_literals

import docker
import gettext
import pathlib
import py
import py.path
import os
import os.path
import sys
import subprocess

from builtins import str
from future.utils import text_to_native_str as native_str
from future.utils import with_metaclass

from ngofile.list_files import list_files
from ngoschema.schema_metaclass import SchemaMetaclass
from ngoschema.classbuilder import ProtocolBase
from ngoschema.decorators import assert_prop

from .project_loader import get_project_loader
from .environment import get_environment
from .python_environment import ToxEnvironment
from .python_environment import PythonEnvironment

_ = gettext.gettext


class Cookiecutter(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaUri = r"http://numengo.org/ngoci/cookiecutter"


class Project(with_metaclass(SchemaMetaclass, ProtocolBase)):
    schemaUri = r"http://numengo.org/ngoci/project"
    _env = None
    _project_loader = None

    def __init__(self, *args, **kwargs):
        ProtocolBase.__init__(self, *args, **kwargs)

    @classmethod
    def project_loader(cls):
        if cls._project_loader is None:
            cls._project_loader = get_project_loader()
        return cls._project_loader

    @classmethod
    def set_project_loader(cls, project_loader):
        cls._project_loader = project_loader

    @classmethod
    def environment(cls):
        if cls._env is None:
            cls._env = get_environment()
        return cls._env

    @classmethod
    def set_environment(cls, environment):
        cls._env = environment

    @classmethod
    def from_loader(cls, name):
        return cls.project_loader().get(name)

    @property
    def envVars(self):
        envs = {
            native_str(k.upper()): native_str(v)
            for k, v in self.environment().envVars.as_dict().items()
        }
        for prj in self.project_loader().objects:
            if prj.repoDir:
                envs[native_str(str(prj.envVarRepoDir).upper())] = native_str(
                    str(prj.repoDir))
        if self.repoDir:
            envs[native_str(str(self.envVarRepoDir).upper())] = native_str(
                str(self.repoDir))
        return envs

    @assert_prop("setup_py")
    def update_from_setup(self):
        pyexepath = py.path.local(sys.executable)
        # special trick to call setdefaultencoding
        # https://stackoverflow.com/questions/2276200/changing-default-encoding-of-python#
        reload(sys)
        sys.setdefaultencoding("UTF8")
        out = pyexepath.sysexec(
            str(self.setup_py),
            "--name",
            "--version",
            "--author",
            "--author-email",
            "--url",
            "--description",
            "--requires",
        )
        o = tuple([o.strip() for o in out.split("\n") if o.strip()])
        name, version, authorName, authorEmail, url, description = o[0:6]
        requires = o[7:]
        self.name = name
        self.version = version
        self.authorName = authorName
        self.authorEmail = authorEmail
        self.website = url
        self.description = description
        self.deps = requires

    @property
    def setup_py(self):
        p = self.repoDir
        if p and p.joinpath("setup.py").exists():
            return p.joinpath("setup.py").resolve()

    @property
    def setup_cfg(self):
        p = self.repoDir
        if p and p.joinpath("setup.cfg").exists():
            return p.joinpath("setup.cfg").resolve()

    @property
    def tox_ini(self):
        p = self.repoDir
        if p and p.joinpath("tox.ini").exists():
            return p.joinpath("tox.ini").resolve()

    @property
    def toxEnv(self):
        if hasattr(self, "_toxEnv"):
            return self._toxEnv
        if self.tox_ini:
            self._toxEnv = ToxEnvironment(self.tox_ini)
            return self._toxEnv

    def bumpversion(self, level="patch"):
        """
        Bump project version harcoded in project files

        :param level: bump to patch/minor/major
        :type level: enum: [patch,minor,major]
        """
        subprocess.Popen("bumpversion %s" % level, cwd=str(self.repoDir))

    def msbuild(self, config="Release", archi="x32"):
        archi = {"x32": "Win32", "x64": "x64"}[archi]

    def clean_imports(self, *args):
        """
        Execute ISORT and autoflake to clean imports in source files
        """
        self.logger.info(_("run ISORT to sort imports"))
        cmds = ["isort", "--verbose", "--recursive"]  # default options
        cmds += [str(a) for a in args]
        srcs = [
            self.repoDir.joinpath(native_str(str(d))) for d in self.dirsSrc
        ]
        tests = [
            self.repoDir.joinpath(native_str(str(d))) for d in self.dirsTest
        ]
        dirs = [str(f) for f in srcs + tests]
        cmds += dirs
        #subprocess.call(cmds)
        self.logger.info(_("run AUTOFLAKE to remove unused imports"))
        cmds = ["autoflake", "-r", "-i"]  # default options
        cmds += [str(a) for a in args]  # should put additional checks

        deps = [
            d._value.split('=')[0].strip() for d in self.depsInstall
            if '/' not in d
        ] if self.depsInstall else []
        deps += ['builtins', 'pytest', str(self.packageName)]
        deps += ['jsonschema', 'python-jsonschema-objects']
        cmds += ["--imports=%s" % (",".join(deps))]

        cmds += dirs
        proc = subprocess.Popen(cmds, cwd=str(self.repoDir))
        proc.wait()

    def format_code(self, *args):
        """
        Execute YAPF to clean imports in source files
        """
        self.logger.info(_("run YAPF to format code"))
        cmds = ["yapf", "-i", "-r", "-e", "*/templates/*"]  # default options
        #self.logger.info(_("run BLACK to format code"))
        #cmds = ["black"]  # default options
        cmds += [str(a) for a in args]
        srcs = [
            self.repoDir.joinpath(native_str(str(d))) for d in self.dirsSrc
        ]
        tests = [
            self.repoDir.joinpath(native_str(str(d))) for d in self.dirsTest
        ]
        cmds += [str(f) for f in srcs + tests]
        proc = subprocess.Popen(cmds, cwd=str(self.repoDir))
        proc.wait()

    def register(self):
        """ register python project on pypi """
        config = self.toxEnv.config
        for f in list_files(config.distdir, "*.whl"):
            subprocess.call(["twine", "register", str(f)])

    def publish(self):
        """ publish python project on pypi """
        config = self.toxEnv.config
        for f in list_files(config.distdir, ["*.whl", "*.gz", "*.zip"]):
            subprocess.call(["twine", "upload", "--skip-existing", str(f)])

    def premake(self, target="vs2017"):
        """ execute premake4 """
        cmds = ["premake5", target]
        proc = subprocess.Popen(
            cmds, cwd=str(self.repoDir), env=self.envVars, shell=True)
        proc.wait()
        for sdir in ['amesim', 'fmi', 'simulink']:
            sdir = self.repoDir.joinpath(sdir)
            if sdir.joinpath('premake5.lua').exists():
                proc = subprocess.Popen(
                    cmds, cwd=str(sdir), env=self.envVars, shell=True)

    def command(self, *cmds):
        if len(cmds) == 1:
            cmds = cmds[0].split(' ')
        proc = subprocess.Popen(
            cmds, cwd=str(self.repoDir), env=self.envVars, shell=True)
        proc.wait()

    def docker(self, *extra_cmds, **options):
        """
        Execute a list of commands on a docker container

        The default image is "numengo/build-x64" but can be changed with options['dockerimage']

        :param cmds: list of commands to run on container
        :type cmds: str
        :param options: options to create container (in docker-py run options)
        """
        dockerimage = options.pop("dockerimage", "numengo/build-x64:latest")
        # find out volumes to expose
        envs_w_path = {
            e: pathlib.Path(v)
            for e, v in self.envVars.items() if '/' in v or '\\' in v
        }
        to_expose = []

        def common_root(p1, p2):
            ret = [p1 for p1, p2 in zip(p1.parts, p2.parts) if p1 == p2]
            if len(ret) > 1:
                return pathlib.Path(*ret)

        for p in envs_w_path.values():
            for r in to_expose:
                if common_root(p, r):
                    to_expose.remove(r)
                    to_expose.append(common_root(p, r))
            if not any([common_root(p, r) for r in to_expose]):
                to_expose.append(p)

        volumes = [
            "%s:/app/%s" % (v.as_posix(), v.relative_to(v.anchor).as_posix())
            for v in to_expose
        ]
        # environment variables
        # 1. envs corresponding to directories in volumes
        environment = [
            "%s=/app/%s" % (e, v.relative_to(v.anchor).as_posix())
            for e, v in envs_w_path.items()
        ]
        # 2. envs which are not paths
        environment += [
            "%s=%s" % (e, v) for e, v in self.envVars.items()
            if '/' not in v and '\\' not in v
        ]

        client = docker.from_env()
        cmd = "&&".join(extra_cmds)
        self.logger.info(_('run command "%s" on %s' % (cmd, dockerimage)))
        #print 'docker run ' + ' '.join(['-v %s'% v for v in volumes]  +['-e "%s"'% e for e in environment] ) + ' %s %s'%(dockerimage, cmd)
        container = client.containers.run(
            dockerimage,
            volumes=volumes,
            detach=True,
            tty=True,
            environment=environment,
            command=cmd,
            **options)
        resp = container.wait()
        logs = container.logs(stdout=True, stderr=True)
        container.stop()
        container.remove()
        if resp["StatusCode"] == 0:
            self.logger.warning(logs)
        else:
            raise Exception(
                "container %s exited with code %i for command %s.\n%s" % (
                    container,
                    resp["StatusCode"],
                    cmd,
                    logs,
                ))

    def docker_build4(self):
        """
        Build the project according to tox.ini or premake
        """
        if self.repoDir.joinpath("premake4.lua").exists():
            self.logger.info(
                _("rebuild distribution according to premake4.lua"))
            wd = self.repoDir.relative_to(self.repoDir.anchor).as_posix()
            self.docker("premake4 gmake", working_dir="/app/%s" % wd)
            self.docker(
                "make config=release64 all", working_dir="/app/%s/build" % wd)
        if self.tox_ini:
            self.logger.info(_("rebuild distribution specified in Tox"))
            config = self.toxEnv.config
            for f in list_files(self.repoDir, "src/*.egg-info/*"):
                os.remove(str(f))
            proc = subprocess.Popen("tox -e check", cwd=str(self.repoDir))
            proc.wait()
            subprocess.call([
                "python",
                str(self.setup_py),
                "sdist",
                "bdist_wheel",
                "--dist-dir",
                str(config.distdir),
            ])

    def docker_build5(self):
        """
        Build the project according to tox.ini or premake
        """
        if self.repoDir.joinpath("premake5.lua").exists():
            self.logger.info(
                _("rebuild distribution according to premake5.lua"))
            wd = self.repoDir.relative_to(self.repoDir.anchor).as_posix()
            self.docker(
                "premake5 gmake --file=premake5.lua",
                working_dir="/app/%s" % wd)
            self.docker(
                "make config=release_x64 all",
                working_dir="/app/%s/build" % wd)
        if self.tox_ini:
            self.logger.info(_("rebuild distribution specified in Tox"))
            config = self.toxEnv.config
            for f in list_files(self.repoDir, "src/*.egg-info/*"):
                os.remove(str(f))
            proc = subprocess.Popen("tox -e check", cwd=str(self.repoDir))
            proc.wait()
            subprocess.call([
                "python",
                str(self.setup_py),
                "sdist",
                "bdist_wheel",
                "--dist-dir",
                str(config.distdir),
            ])
