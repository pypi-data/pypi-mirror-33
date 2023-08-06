# coding: utf-8

from __future__ import print_function, absolute_import, division, unicode_literals

import sys
import os                 # NOQA

from ruamel.std.argparse import ProgramBase, option, CountAction, \
    SmartFormatter, sub_parser, version
from ruamel.appconfig import AppConfig
from . import __version__
from .develop import Develop


def to_stdout(*args):
    sys.stdout.write(' '.join(args))


alt_names = dict(
    dvm='make',
    dvt='tox',
    dvpt='pytest',
    dv8='flask8',
    dvr='repo',  # hg/git
    dvv='version',  # hg/git
)


class DevelopCmd(ProgramBase):
    def __init__(self):
        cmd = sys.argv[0].rsplit('/', 1)[-1]
        alt = alt_names.get(cmd)
        if alt:
            sys.argv.insert(1, alt)
        super(DevelopCmd, self).__init__(
            formatter_class=SmartFormatter,
            # aliases=True,
            # usage="""""",
        )

    # you can put these on __init__, but subclassing DevelopCmd
    # will cause that to break
    @option('--verbose', '-v',
            help='increase verbosity level', action=CountAction,
            const=1, nargs=0, default=0, global_option=True)
    @option(
        '--distbase',
        help='base directory for all distribution files (default: %(default)s)')
    @option('--keep', help='keep temporary files', action='store_true', global_option=True)
    @version('version: ' + __version__)
    def _pb_init(self):
        # special name for which attribs are included in help
        pass

    def run(self):
        if self._args.distbase:
            # where the distribution files live
            os.environ['PYDISTBASE'] = self._args.distbase
        self.develop = Develop(self._args, self._config)
        if hasattr(self._args, 'func'):  # not there if subparser selected
            return self._args.func()
        self._parse_args(['--help'])     # replace if you use not subparsers

    def parse_args(self):
        self._config = AppConfig(
            'develop',
            filename=AppConfig.check,
            parser=self._parser,  # sets --config option
            warning=to_stdout,
            add_save=True,  # add a --save-defaults (to config) option
        )
        # self._config._file_name can be handed to objects that need
        # to get other information from the configuration directory
        self._config.set_defaults()
        self._parse_args(
            # default_sub_parser="",
        )

    @sub_parser(help='clean up development directory')
    @option('args', nargs='*')
    def clean(self):
        self.develop.clean()

    @sub_parser(help='execute dist related commands')
    def dist(self):
        self.develop.dist()

    @sub_parser(help='invoke make (with args), writes .Makefile.tmp')
    @option('args', nargs='*')
    def make(self):
        self.develop.make()

    @sub_parser(help='invoke mypy --strict')
    # @option('args', nargs='*')
    def mypy(self):
        self.develop.mypy()

    @sub_parser(help='create and push a new release')
    @option('--test', action='store_true', help="test only don't push to PyPI")
    @option('--changestest', action='store_true', help='test update of CHANGES')
    @option('--reuse-message', '--re-use-message',
            action='store_true', help='reuse commit message')
    @option('--no-tox', action='store_true', help="don't run tox -r")
    def push(self):
        self.develop.push()

    @sub_parser(help='execute Read the Docs related commands')
    @option('--build', action='store_true', help="trigger build")
    def rtfd(self):
        self.develop.rtfd()

    @sub_parser(help='invoke tox (with args)')
    @option('-e', metavar='TARGETS', help='only test comma separated %(metavar)s')
    @option('args', nargs='*')
    def tox(self):
        self.develop.tox()

    @sub_parser(help='execute version related commands')
    @option('args', nargs='*')
    def version(self):
        self.develop.version()


def main():
    n = DevelopCmd()
    n.parse_args()
    sys.exit(n.run())


if __name__ == '__main__':
    main()
