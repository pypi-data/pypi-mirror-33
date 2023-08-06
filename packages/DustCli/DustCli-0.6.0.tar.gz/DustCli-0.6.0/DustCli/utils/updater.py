from cement.utils import shell
from pathlib import Path
import datetime


class Updater:

    @staticmethod
    def check_and_update(force=False):
        if not Path.home().joinpath('.dust').exists():
            return
        path = Path.home().joinpath('.dust', '.version-check')
        if not path.exists():
            with open(str(path), 'w+') as f:
                f.write('0')

        with open(str(path)) as f:
            lines = f.readlines()
            if len(lines) <= 0:
                lines.append('0')

        time = float(lines[0])
        now = datetime.datetime.now().timestamp()

        if not force and now - time <= 86400:
            return

        print('正在检查版本...')
        shell.exec_cmd2(['pip3', 'install', '--upgrade', 'DustCli', '--no-cache-dir', '-q'])
        print('版本检查完成')
        with open(str(path), 'w+') as f:
            f.write(str(now))
