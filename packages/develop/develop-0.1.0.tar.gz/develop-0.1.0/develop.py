# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

"""
develop (dv, dvm, dvt) is a wrapper around programs like hg,
make, tox, pytest, devpi, flask8, etc that creates "missing" files
from information in __init__.py, then runs the program and deletes
those "missing" files. It prevents clutter and single source
configuration.

It replaces several options that were only

- Makefile doesn't need to get version using "python setup.py --version", which is slow

ToDo:
- more intelligent pushing of dist files to other servers

"""

import sys
import os
import io
import subprocess
from datetime import date
from contextlib import ContextDecorator

from pon import PON
from ruamel.std.pathlib import Path, pushd, popd
from ruamel.showoutput import show_output

initpy = '__init__.py'


versions = {
    'py26': [9, date(2013, 10, 29)],
    'py27': [13, None],
    'py30': [1, date(2009, 2, 13), ],
    'py31': [5, date(2012, 6, 30),
             'https://www.python.org/dev/peps/pep-0375/#maintenance-releases'],
    'py32': [7, date(2016, 2, 28), 'https://www.python.org/dev/peps/pep-0392/#lifespan'],
    'py33': [7, date(2017, 9, 30), 'https://www.python.org/dev/peps/pep-0398/#lifespan'],
    'py34': [6, None, 'https://www.python.org/dev/peps/pep-0429/'],
    'py35': [3, None, 'https://www.python.org/dev/peps/pep-0478/'],
    'py36': [1, None, 'https://www.python.org/dev/peps/pep-0494/'],
}


mit_license = """\
 The MIT License (MIT)

 Copyright (c) {year} {fullname}

 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:

 The above copyright notice and this permission notice shall be included in
 all copies or substantial portions of the Software.

 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
"""


class TmpFiles(ContextDecorator):
    def __init__(self, parent,
                 setup=True, license=True, tox=False, makefile=False):
        self._rm_after = []
        self.parent = parent
        self.setup = setup
        self.license = license
        self.tox = tox
        self.makefile = makefile
        self.keep = parent._args.keep
        self.pon = self.parent.pon  # trigger any check on pon

    def __enter__(self):
        if self.setup:
            target = Path('~/.config/develop/setup.py').expanduser()
            p = Path('setup.py')
            if not p.exists():
                # p.symlink_to(target)
                target.copy(p)
            self._rm_after.append(p)
        if self.license:
            lic = self.pon.obj.get('license')
            if lic is None or 'MIT' in lic:
                plic = Path('LICENSE')
                start_year = self.pon.obj['since']  # has to be in __init__.py
                this_year = date.today().year
                if start_year != this_year:
                    year = '{}-{}'.format(start_year, this_year)
                else:
                    year = this_year
                plic.write_text(mit_license.format(
                    year=year,
                    fullname='Anthon van der Neut, Ruamel bvba'))
                self._rm_after.append(plic)
        _tox = self.pon.obj.get('tox')
        if self.tox and _tox is None:
            print('no tox specification in __init__.py')
        # print('tox:', _tox)
        if self.tox and _tox is not None:
            t = Path('tox.ini')
            with t.open('w') as fp:
                print('[tox]', file=fp)  # NOQA
                envlist = ['pep8']
                e = str(_tox['env'])
                # env 3 -> latest 3, 2 -> latest 2, * all active, p -> pypy, j -> jython
                if '3' in e:
                    envlist.append('py36')
                if '2' in e:
                    envlist.append('py27')
                if '*' in e:
                    envlist.extend(['py36', 'py27', 'py35', 'py34'])
                if 'p' in e:
                    envlist.append('pypy')
                if 'j' in e:
                    envlist.append('jython')
                print('envlist = {}'.format(','.join(envlist)), file=fp)
                print('\n[testenv]', file=fp)
                print('commands =', file=fp)
                print("    /bin/bash -c 'pytest _test/test_*.py'", file=fp)
                print('deps =', file=fp)
                # deps extra dependency packages for testing
                # deps = ['pytest', 'flake8==2.5.5']
                deps = ['pytest', 'flake8==3.3.0']
                tdeps = _tox.get('deps', [])
                if isinstance(tdeps, str):
                    deps.extend(tdeps.split())
                else:
                    deps.extend(tdeps)
                for dep in deps:
                    print('    {}'.format(dep), file=fp)
                # [pytest]
                # norecursedirs = test/lib .tox
                print('\n[testenv:pep8]', file=fp)
                print('commands =', file=fp)
                subdirs = ['.tox']
                if self.parent.sub_packages:
                    subdirs.extend(self.parent.sub_packages)
                if subdirs:
                    subdirs = ' --exclude ' + ','.join(subdirs)
                print('    flake8 {}{{posargs}}'.format(subdirs), file=fp)
                # fl8excl extra dirs for exclude
                print('\n[flake8]', file=fp)
                print('show-source = True', file=fp)
                print('max-line-length = 95', file=fp)
                # the following line was in tox.ini for pon
                # E251 is space around keyword?
                # print('ignore = E251', file=fp)
                excl = _tox.get('fl8excl', '')
                if excl and isinstance(excl, str):
                    excl = ','.join(excl.split()) + ','
                elif excl:
                    excl = ','.join(excl) + ','
                print('exclude = {}.hg,.git,.tox,dist,.cache,__pycache__,'
                      'ruamel.zip2tar.egg-info'.format(excl), file=fp)
                self._rm_after.append(t)
        if self.makefile:
            fpn = self.pon.obj['full_package_name']
            util_name = fpn.rsplit('.', 1)[-1]
            version = self.pon.obj['__version__']
            versiond = version + '0' if version.endswith('.dev') else version
            m = Path('.Makefile.tmp')
            if False:
                mt = Path('Makefile.tmp')
                if m.exists() and not mt.exists():
                    m.rename(mt)
            with m.open('w') as fp:
                print('\nUTILNAME:={}'.format(util_name), file=fp)
                print('PKGNAME:={}'.format(fpn), file=fp)
                print('INSTPKGNAME:=--pkg {}'.format(fpn), file=fp)
                print('VERSION:={}'.format(version), file=fp)
                print('VERSIOND:={}'.format(versiond), file=fp)
                # print('\ninclude ~/.config/ruamel_util_new/Makefile.inc', file=fp)
                print('\ninclude ~/.config/develop/Makefile.inc', file=fp)
                # print('\nclean: clean_common', file=fp)  # replaced by dv clean
            self._rm_after.append(m)
        return self

    def __exit__(self, typ, value, traceback):
        if typ:
            print('typ', typ)
        if self.keep:
            return
        for p in self._rm_after:
            p.unlink()


class DevelopError(Exception):
    pass


class Log:
    def __init__(self):
        pass

    def __enter__(self):
        print("__enter__")
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        print("__exit__")


PKG_DATA = '_package_data'


class Develop:
    def __init__(self, args, config):
        self._args = args
        self._config = config
        self.old_dist_dir = Path('dist')

    @property
    def pon(self):
        attr = '_' + sys._getframe().f_code.co_name
        if not hasattr(self, attr):
            pon = PON()
            with io.open(initpy) as fp:
                pon.extract(fp, start=PKG_DATA)
                check_init_pon(initpy, pon)
            setattr(self, attr, pon)
        return getattr(self, attr)

    def tox(self):
        with TmpFiles(self, tox=True):
            try:
                args = self._args.args
                if self._args.e:
                    args = ['-e', self._args.e] + args
                res = show_output(['tox'] + args, show_command=True)
            except subprocess.CalledProcessError:
                return
            print('res:', res)

    def mypy(self):
        # we could have files in subdirectories that need inclusion, and
        # for that you have to walk the subtree, skip any sub-packages
        # base on their __init__.py:_package_data['nested']
        # for now (ruamel.yaml) solve as the Makefile did
        # MYPYSRC:=$(shell ls -1 *.py | grep -Ev "^(setup.py|.*_flymake.py)$$" | \
        #    sed 's|^|ruamel/yaml/|')
        # MYPYOPT:=--py2 --strict --follow-imports silent
        #
        # mypy:
        # 	@echo 'mypy *.py'
        # 	@cd ../.. ; mypy $(MYPYOPT) $(MYPYSRC)
        # 	mypy $(MYPYOPT) $(MYPYSRC1)
        options = ['--py2', '--strict', '--follow-imports', 'silent']
        fpn_split = self.pon.obj['full_package_name'].split('.')
        _root_dir = '/'.join(['..'] * len(fpn_split))
        pushd(_root_dir)
        pkg_path = Path('/'.join(fpn_split))
        files = []
        for path in pkg_path.glob('*.py'):
            if path.name == 'setup.py':  # might not be there
                continue
            if path.stem.endswith('_flymake'):
                continue
            files.append(path)
            # print(' ', path)
        # print(len(files))
        res = show_output(['mypy'] + options + files, verbose=True, show_command='\\')
        if res:
            print(res)
        popd()

    def make(self):
        try:
            util_name = self.pon.get('util')
            if util_name:
                os.environ['OPTUTILNAME'] = util_name
        except KeyError:
            pass
        try:
            entry_points = self.pon.get('entry_points')  # NOQA
        except KeyError:
            pass
        self.check_dist_dir()
        self.use_alternative('clean')
        with TmpFiles(self, makefile=True):
            if self._args.args:
                try:
                    res = show_output(['make', '-f', '.Makefile.tmp'] + self._args.args)
                    res = None  # NOQA
                except subprocess.CalledProcessError:
                    sys.exit(0)

    def use_alternative(self, alternatives):
        if not isinstance(alternatives, list):
            alternatives = [alternatives]
        try:
            arg0 = self._args.args[0]
        except IndexError:
            return None
        if arg0 and arg0 in alternatives:
            print('Use:\n   dv {}\n.'.format(self._args.args[0]))
            sys.exit(1)
        return False

    def version(self):
        """
        this currently directly calls the various (package)version commands
        (-> direct dv replacement if available):

        show                show current version
        bump                bump version number if equal to latest on PyPI
        major               bump minor version number
        minor               bump minor version number
        micro               bump micro version number
        dev                 set/unset dev
        update              update to preferred __init__.py etc
        license             update license info
        status              check status of project
        push                check, commit, push, upload and bump if everything ok
        bitbucket           create/check bitbucket
        test                test package setup (conformity, pypi, bitbucket)

        "dvv" equals "dv version" use "dvv -- push --reuse --no-tox" to end commandline
        interpretation
        """
        if self._args.args and self._args.args[0] == 'push':
            print('Use:\n   dv {}\n'.format(self._args.args[0]))
            # with TmpFiles(self, license=True, tox=True, makefile=True):
            #     self.do_version()
            return
        self.do_version()

    def clean(self):
        cmds = [
            'rm -rf build .tox {}.egg-info/ README.pdf _doc/*.pdf _doc/_build'.format(
                self.pon.obj['full_package_name']),
            'find . -name "*.pyc" -exec rm {} +',
            'find . -name "*~" -exec rm {} +',
            'find . -name "*.orig" -exec rm {} +',
            'find . -name "__pycache__" -print0  | xargs -r -0 rm -rf',
        ]
        for cmd in cmds:
            print(cmd)
            os.system(cmd)

    def rtfd(self):
        if self._args.build:
            prj = self.pon.obj['read_the_docs']
            os.system('curl -X POST https://readthedocs.org/build/{}'.format(prj))
            return
        print('rtfd what?')

    def push(self):
        self.check_dist_dir()
        with TmpFiles(self, license=True, tox=True, makefile=True):
            cmd = ['version', 'push']
            if self._args.reuse_message:
                cmd.append('--reuse-message')
            if self._args.no_tox:
                cmd.append('--no-tox')
            if self._args.test:
                cmd.append('--test')
            if self._args.changestest:
                cmd.append('--changestest')
            os.system(' '.join(cmd))
        self.build_rtfd_doc()
        if self.old_dist_dir.exists():
            # manylinux1 currently creates this
            try:
                self.old_dist_dir.rmdir()
            except:
                print('cannot remove "{}"'.format())

    def do_version(self):
        # show_output(sys.argv[1:])
        cmd = 'version ' + ' '.join(self._args.args)
        # print('cmd:', cmd)
        os.system(cmd)  # so you can edit

    def dist(self):
        dist_dir = self.check_dist_dir()
        pkg = self.pon.obj['full_package_name']
        versions = {}
        for fn in dist_dir.glob(pkg + '-*'):
            version = fn.stem[len(pkg) + 1:]
            v = xversion(version)
            versions.setdefault(v, []).append(fn)
        # mm = None
        count = 0
        for version in sorted(versions, reverse=True):
            print(str(version))
            for fn in sorted(versions[version]):
                print(' ', fn.name)
            count += 1
            if count > 2:
                break
            # major, minor = get_mm(version)
            # if mm is None:
            #     mm = (major, minor)
            # elif mm[0] != major or mm[1] != minor:
            #     break
        print("+", len(versions) - count)

    def build_rtfd_doc(self):
        import requests
        # rtfd is the internal number on readthedocs, inspect the [Build] button
        rtfd_id = self.pon.obj.get('rtfd')
        if rtfd_id:
            if not isinstance(rtfd_id, int):
                raise NotImplementedError
            url = 'http://readthedocs.org/build/{}/'.format(rtfd_id)
            # no login necessary
            r = requests.post(url, data={'submit': 'build'})  # NOQA

    def check_dist_dir(self):
        if not self._args.distbase:
            print("you have to set --distbase")
            sys.exit(-1)
        pkg = self.pon.obj['full_package_name']
        dist_dir = Path(self._args.distbase) / pkg
        if not dist_dir.exists():
            dist_dir.mkdir(parents=True)
            if self.old_dist_dir.exists():
                for fn in self.old_dist_dir.glob('*'):
                    fn.copy(dist_dir / fn.name)
                    fn.unlink()
                self.old_dist_dir.rmdir()
        else:
            if self.old_dist_dir.exists():
                print('cannot have both {} and {}'.format(dist_dir, self.old_dist_dir))
                sys.exit(-1)
        return dist_dir

    @property
    def sub_directory_pon(self):
        # list of subdirectories that have __init__.py and obtionally pon (if not -> None)
        attr = '_' + sys._getframe().f_code.co_name
        if not hasattr(self, attr):
            pons = {}
            for path in Path('.').glob('*/' + initpy):
                try:
                    with io.open(path) as fp:
                        pon = PON()
                        if pon.extract(fp, start=PKG_DATA) is None:
                            pon = None
                        else:
                            check_init_pon(path, pon)
                except IOError:
                    pon = None
                pons[str(path.parent)] = pon
            setattr(self, attr, pons)
        return getattr(self, attr)

    @property
    def sub_packages(self):
        ret_val = []
        for path in self.sub_directory_pon:
            pon = self.sub_directory_pon[path]
            if pon and pon.obj.get('nested'):
                ret_val.append(path)
        return ret_val


def x1version(version):
    from cmp_version import VersionString

    class MyVS(VersionString):
        def __hash__(self):
            return hash(str(self))

    dv = version.split('.tar', 1)[0]
    dv = dv.split('-cp', 1)[0]
    dv = dv.split('-py', 1)[0]
    dv = dv.replace('.dev0', '.a0')

    v = MyVS(dv)
    if 'xxdev' in version:
        print(v, repr(v))
    return v
    return
    from .version import Version

    version = version.replace('.dev0', '.a')
    v = Version(version)
    if 'alph' in version:
        print(v, repr(v))
    return v
    ret = []
    for n in version.replace('-', '.', 1).split('.'):
        try:
            ret.append('{:03d}'.format(int(n)))
        except ValueError:
            ret.append(n)
    return tuple(ret)


def xversion(version):
    # use verlib?
    # pip has semantic versioning as well, verlib does
    from pip._vendor.distlib.version import NormalizedVersion

    dv = version.split('.tar', 1)[0]
    dv = dv.split('-cp', 1)[0]
    dv = dv.split('-py', 1)[0]

    return NormalizedVersion(dv)
    # print(dir(v))
    # print(v._parts)


def check_init_pon(path, pon):
    irs = pon.obj.get('install_requires', [])
    if isinstance(irs, dict):
        if 'any' in irs:
            if len(irs) == 1:
                pon.obj['install_requires'] = irs['any']
                pon.update(path, start=PKG_DATA)
            else:
                raise NotImplementedError('install_requires should be a list')
    ep = pon.obj.get('entry_points')
    if ep:
        for ir in irs:
            if ir.startswith('ruamel.std.argparse'):
                try:
                    v = ir.split('>=')[1]
                except:
                    try:
                        v = ir.split('>')[1]
                    except:
                        v = '0.1'
                v = tuple(map(int, v.split('.')))
                min_ver = (0, 8)
                if not v >= min_ver:
                    print('need at least version {} < {} in {} for ruamel.std.argparse'.format(
                        str(v), str(min_ver), path))
                    sys.exit(1)
    # print('ep', ep)
    #        v = list(p.obj['version_info'])
    #        v[1] += 1 # update minor version
    #        v[2] = 0 # set micro version
    #        p.obj['version_info'] = tuple(v)
    #        p.update(file_name, start=s, typ=t)


# def get_mm(v):
#     return v._parts[1][0], v._parts[1][1]
