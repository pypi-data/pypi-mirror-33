"""DustCli bootstrapping."""

from DustCli.utils.updater import Updater
from DustCli.utils.arg_parser import ArgParser

from cement.ext.ext_argparse import ArgparseArgumentHandler
from DustCli.cli.controllers.base import BaseController
from DustCli.cli.controllers.project import ProjectController, SDKController
from DustCli.cli.controllers.package import PackageController
from DustCli.cli.controllers.ci import CIController
from DustCli.cli.controllers.mr import MRController
from DustCli.cli.controllers.lint import LintController


class ModifiedArgparseArgumentHandler(ArgparseArgumentHandler):
    class Meta:
        label = 'dust_arg_parse'
        ignore_unknown_arguments = True

    def __init__(self, *args, **kw):
        super(ModifiedArgparseArgumentHandler, self).__init__(*args, **kw)

    def parse(self, arg_list):
        if self._meta.ignore_unknown_arguments is True:
            args, unknown = self.parse_known_args(arg_list)
            self.parsed_args = args
            for arg in unknown:
                if arg.startswith('_dust_parse'):
                    r = ArgParser.eval(arg)
                    unknown[unknown.index(arg)] = r
            self.unknown_args = unknown
        else:
            args = self.parse_args(arg_list)
            self.parsed_args = args
        return self.parsed_args


def load(app):
    Updater.check_and_update()
    app.handler.register(ModifiedArgparseArgumentHandler)
    app.handler.register(BaseController)
    app.handler.register(ProjectController)
    app.handler.register(SDKController)
    app.handler.register(PackageController)
    app.handler.register(CIController)
    app.handler.register(MRController)
    app.handler.register(LintController)
