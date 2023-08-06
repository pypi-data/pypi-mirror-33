import subprocess
from cement.utils import shell
import shutil


class GitUtil(object):

    @staticmethod
    def clone(git, to_path, clean=True):
        if clean:
            if to_path.is_dir():
                shutil.rmtree(str(to_path))
        elif to_path.is_dir():
            return

        shell.exec_cmd2(['git', 'clone', git, str(to_path)])

    # 是否在git目录
    @staticmethod
    def is_git():
        return subprocess.getoutput('git status | grep "Not a git repository"') == ''

    # fetch
    @staticmethod
    def fetch():
        return subprocess.getoutput('git fetch')

    # 获取项目空间名
    @staticmethod
    def get_project_name():
        remote = subprocess.getoutput('git config --get remote.origin.url')
        
        if remote.find('.com/') >=0:
            project_name = remote.split('.com/')[1]
        elif remote.find('.com:') >=0:
            project_name = remote.split('.com:')[1]
        else:
            return ''

        return project_name.split('.git')[0].replace('/', '%2F')

    # 获取当前所在分支
    @staticmethod
    def get_current_branch():
        current_branch = subprocess.getoutput('git branch | grep "*"')
        if current_branch == '':
            return False
        return current_branch.split('* ')[1].split("\n")[0]

    # 获取 branch 上HEAD的commit id
    @staticmethod
    def get_head_commit(branch):
        return subprocess.getoutput('git rev-parse ' + branch)

    # branch是否存在 todo不严谨，待正则匹配
    @staticmethod
    def branch_is_exit(branch):
        return subprocess.getoutput('git branch -r | grep ' + branch) != ''


if __name__ == "__main__":
    print('Test current branchName: ' + GitUtil.get_current_branch())
    print('Test get_head_commit: ' + GitUtil.get_head_commit('origin/test'))
