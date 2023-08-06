"""DustCli base controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from cement.utils import shell
from DustCli.utils.updater import Updater
from pathlib import Path
import os
from DustCli.utils.version import version


class BaseController(ArgparseController):
    class Meta:
        label = 'base'
        description = '大搜车前端项目脚手架'
        arguments = [
            (['-v', '--version'],
             dict(action='store_true', help='版本号'),
             ),
        ]

    @expose(hide=True)
    def default(self):
        if self.app.pargs.version:
            self.app.log.info(version)
        else:
            os.system('dust --help')

    @expose(help="初始化")
    def init(self):
        path = str(Path.home()) + '/.dust'
        if Path(path).is_dir():
            self.app.log.info('已经完成初始化，请勿重复初始化')
            return
        stdout, stderr, exitcode = shell.exec_cmd(['mkdir', path])
        if exitcode == 0:
            self.app.log.info('初始化成功')
            shell.exec_cmd2(['dust', '--help'])
        else:
            self.app.log.fatal("初始化失败: %s" % stderr)

    @expose(help='更新')
    def update(self):
        Updater.check_and_update(force=True)
