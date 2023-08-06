"""DustCli mr controller."""

from cement.ext.ext_argparse import ArgparseController, expose
from pathlib import Path
from DustCli.core.bundle import Bundle
from DustCli.core.merge import Merge
import os
from DustCli.utils.git import GitUtil
from DustCli.utils.api_client import Api

import gitlab
from DustCli.utils.git_token import set_token

class MRController(ArgparseController):
    class Meta:
        label = 'mr'
        description = 'MergeRequest相关命令'
        stacked_on = 'base'
        stacked_type = 'nested'
        arguments = [
            (['-b', '--branch'],
             dict(action='store', help="指定目标分支名称")),
            (['-m', '--message'],
             dict(action='store', help="指定MR标题")),
            (['-t', '--token'],
             dict(action='store', help="指定gitlab Private token")),
        ]

    @expose(hide=True)
    def default(self):
        pargs = self.app.pargs

        token = pargs.token
        branch = pargs.branch
        title = pargs.message

        if token:
            set_token(token)
            return

        if not branch:
            if not title:
                os.system('dust mr -h')
                return
                
            self.app.log.warning('请指定目标分支名称 -b={branch}')
            return

        if not title:
            self.app.log.warning('请指定MR标题 -m={message}')
            return

        self.create_mr(branch, title)

    # 创建mr
    def create_mr(self, target_branch, title):
        git = GitUtil()
        target_branch = target_branch.replace('origin/','')

        # 不在git目录下
        if git.is_git() == False:
            self.app.log.error('不在git目录下')
            return

        # 不存在远程
        current_branch = git.get_current_branch()
        if not current_branch:
            self.app.log.error('找不到remote')
            return

        git.fetch()

        # current_branch远程不存在
        if git.branch_is_exit('origin/' + current_branch) == False:
            self.app.log.error(current_branch + '远程不存在')
            return

        # target_branch远程不存在
        if git.branch_is_exit('origin/' + target_branch) == False:
            self.app.log.error(target_branch + '远程不存在')
            return

        # current_branch与target_branch在同一个commit
        current_branch_head_commit = git.get_head_commit('origin/' + current_branch)
        target_branch_head_commit = git.get_head_commit('origin/' + target_branch)
        if current_branch_head_commit == target_branch_head_commit:
            self.app.log.error(current_branch + '与' + target_branch + '在同一个commit')
            return

        project_name = git.get_project_name()
        if project_name == '':
            self.app.log.error('Git remote url找不到，请确认是否存在remote!')
            return

        try:
            api = Api(project_name)
            mr = api.create_mr(current_branch, target_branch, title)
            print('创建成功: '+mr.web_url)
        except gitlab.GitlabGetError as e:
            self.app.log.error('创建MR失败：' + str(e) + '\n请检查是否设置有效的Private token，使用dust mr -t={token}设置token')
        except gitlab.GitlabCreateError as e:
            self.app.log.error('创建MR失败：' + str(e) + '\n请检查Private token是否有创建权限，使用dust mr -t={token}设置token')
        except Exception as e:
            self.app.log.error(e)
       
