"""DustCli lint controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from cement.utils import shell
import getpass
from pathlib import Path
import os
import json
from DustCli.utils.traceid_lint import TraceidLinter


class LintController(ArgparseController):
    class Meta:
        label = 'lint'
        description = '代码 lint 相关命令'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = []
        
    @expose(hide=True)
    def default(self):
        os.system('dust lint -h')

    @expose(help='检查 traceId',
            arguments=[
                (['-g', '--git'],
                 dict(action='store', help='git 地址')
                 ),
                (['-b', '--branch'],
                 dict(action='store', help='分支名')
                 ),
                (['-G', '--group'],
                 dict(action='store', help='项目组地址')
                 ),
                (['-f', '--format'],
                 dict(action='store', help='输出格式，支持 json 和 html')),
                (['-c', '--current'],
                 dict(action='store_true', help='在当前目录下验证')
                 )
            ])
    def trace_id(self):
        if self.app.pargs.group:
            name = None
            gitlab_path = Path.home().joinpath('.dust', '.gitlab')
            if gitlab_path.exists():
                with open(str(gitlab_path)) as f:
                    content = f.read()
                if content:
                    info = json.loads(content)
                    name = info['name']
                    psw = info['psw']
            if not name:
                name = shell.Prompt("输入你 gitlab 登录的邮箱").input
                psw = getpass.getpass('输入你 gitlab 的密码:')
            self.app.log.warning('从 group 统计只会统计在 master 上的代码')
            format = self.app.pargs.format if self.app.pargs.format else 'html'
            path = TraceidLinter.lint_group(self.app.pargs.group, name, psw, format)
            self.app.log.info('统计结果保存地址: %s' % path)
        else:
            if not self.app.pargs.git:
                self.app.log.info('请指定项目 git 地址')
                return
            branch = 'master' if not self.app.pargs.branch else self.app.pargs.branch
            (passed, msg) = TraceidLinter.lint_git(self.app.pargs.git, branch)
            if passed:
                self.app.log.info(msg)
            else:
                self.app.log.error(msg)
