"""DustCli ci controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from pathlib import Path
from cement.utils import shell
import os
from DustCli.utils.git import GitUtil
import shutil
from shutil import ignore_patterns
from DustCli.utils.dust_exec import DustExec
import requests

ciPath = Path.home().joinpath('.dust', 'ci-scripts')


class CIController(ArgparseController):
    class Meta:
        label = 'ci'
        description = '持续集成相关命令'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = []

    @expose(hide=True)
    def default(self):
        os.system('dust ci --help')

    @expose(help="初始化 CI 命令：从 gitlab 下载 python 脚本",
            arguments=[
                (['-n', '--name'],
                 dict(action='store', help='脚本集的名称，例如：ci-script-for-destiny')
                 ),
                (['-g', '--git'],
                 dict(action='store', help='git 仓库的名称，例如: standard-swift-ci-scripts')
                 ),
            ])
    def init(self):
        git = self.app.pargs.git
        name = self.app.pargs.name
        if not name:
            self.app.log.error('请设置一个名字')
            return

        if not git and not self.app.args.unknown_args:
            self.app.log.error('请设置 git 地址')
            return

        target_path = ciPath.joinpath(name)
        if target_path.is_dir():
            shutil.rmtree(str(target_path))
        os.makedirs(str(target_path))

        self.app.args.unknown_args.append(git)
        repos = self.app.args.unknown_args
        file_from = {}
        for arg in repos:
            git_path = 'git@git.souche-inc.com:SCFEE/CI-Scripts/%s.git' % arg
            path = Path.home().joinpath('.dust', arg)
            GitUtil.clone(git_path, path)
            self.app.log.info('clone %s 完成' % arg)

            for file_name in os.listdir(str(path)):
                if file_name == '.git':
                    continue

                full_file_name = path.joinpath(file_name)
                file_target_path = target_path.joinpath(file_name)
                if file_target_path.exists():
                    self.app.log.info('文件 %s 重复：' % file_name)
                    options = [
                        '来自 %s ,已经存在' % file_from[file_name],
                        '来自 %s' % arg,
                    ]
                    source = shell.Prompt(
                        "选择使用哪个版本的文件：",
                        options=options,
                        numbered=True,
                    ).input
                    skip_copy = source in options
                    if skip_copy:
                        continue
                    else:
                        shutil.rmtree(str(file_target_path))

                shutil.copyfile(str(full_file_name), str(file_target_path))
                file_from[file_name] = arg

    @expose(help="运行 CI 命令",
            arguments=[
                (['-n', '--name'],
                 dict(action='store', help='脚本组的名字'),
                 ),
                (['-s', '--script'],
                 dict(action='store', help='脚本名称'),
                 ),
            ])
    def run(self):
        name = self.app.pargs.name
        script = self.app.pargs.script
        if not name:
            self.app.log.error('请设置脚本组的名字')
            return
        if not script:
            self.app.log.error('请设置要运行的脚本')
            return

        script_path = ciPath.joinpath(name, script + '.py')
        with open(str(script_path)) as f:
            error_handler = (lambda msg: self.app.log.error(msg))
            result = DustExec.exec(ciPath.joinpath(name), f.read(), self.app.args.unknown_args, error_handler)
        if result:
            print(result)

    @expose(help="发起主动 CI 集成，完成后开放 tag",
            arguments=[
                (['-j', '--job'],
                 dict(action='store', help='任务名称')
                 )
            ])
    def manual(self):
        job_name = self.app.pargs.job
        if not job_name:
            self.app.info.error('job 未指定')
            return

        if not GitUtil.get_current_branch() == 'master':
            self.app.log.warning('当前不在 master 分支，该操作仅对 master 分支有效')

        choose = shell.Prompt('当前不在 master 分支，该操作仅对 master 分支有效，是否继续操作 (y/n)?', default='y').input
        if not choose == 'y':
            return

        self.app.log.info('请确保改项目已配置 CI 的 web hook')
