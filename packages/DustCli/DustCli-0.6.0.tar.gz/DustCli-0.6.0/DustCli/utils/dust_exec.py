from pathlib import Path

group_path = Path()


def exec_file(name):
    global group_path
    script_path = group_path.joinpath(name + '.py')
    if not script_path.exists():
        return None

    with open(str(script_path)) as f:
        exec(f.read(), globals())
    return globals().get('dust_main', None)


class DustExec:
    @staticmethod
    def exec(path, string, params, error_handler):
        global group_path
        group_path = path
        exec(string, globals())
        main = globals().get('dust_main', None)
        if not main:
            error_handler('没有找到 dust_main 入口')
            return None
        return main(*params)
