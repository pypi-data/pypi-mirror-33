import os
import re
import glob
from pathlib import Path
from DustCli.utils.version_cls import Version
from gitlab import Gitlab
from cement.utils import shell
import json


class TraceidLinter:

    @staticmethod
    def lint_path(project_path):
        package_path = project_path.joinpath('package.json')
        gradles = [p for p in glob.glob(str(project_path) + "/**/*.gradle", recursive=True) if Path(p).exists()]
        version = None
        passed = False
        msg = None
        if package_path.exists():
            with open(str(package_path)) as f:
                content = f.read()
            match = re.search('"@souche-f2e/srn-framework":\s?"\^?[0-9]+.[0-9]+.[0-9]+', content)
            framework = "rn: @souche-f2e/srn-framework"
            min_version = Version('0.3.3')
            if not match:
                match = re.search('"@souche-f2e/http-request":\s?"\^?[0-9]+.[0-9]+.[0-9]+', content)
                framework = "h5: @souche-f2e/http-request"
                min_version = Version('2.1.0')
            else:
                appjs_path = project_path.joinpath('src', 'App.js') if project_path.joinpath('src', 'App.js').exists() else project_path.joinpath('src', 'app.js')
                if appjs_path.exists():
                    with open(str(appjs_path)) as f:
                        content = f.read()
                    content = content.replace(' ', '').replace('\n', '').replace('\r', '')
                    if re.search("SRNFetch[^']*?\}from'@souche-f2e\/srn-util';", content):
                        os.system('rm -rf %s' % str(project_path))
                        return False, 'RN 项目使用老版本的 srn-util, 请使用 srn-framework 0.3.3 以上版本'
            if match:
                version = Version(match.group(0).split(':')[1].replace('"', '').replace('^', '').strip())
            else:
                (passed, msg) = False, '没有找到 TraceId 暴露的库，RN 请引用 @souche-f2e/srn-framework 0.3.3 以上版本, H5 请引用 ' \
                                       '@souche-f2e/http-request 2.1.0 以上版本'
        else:
            print(">> 没有找到 package.json 文件，开始查找安卓 *.gradle 文件")
            android_match = None
            for gradle in gradles:
                with open(gradle) as f:
                    content = f.read()
                match = re.search("rxvm2\s?[:=]\s?'?[0-9]+.[0-9]+.[0-9]+", content)
                framework = "android-rx: rxvm2"
                min_version = Version('0.4.3')
                if not match:
                    match = re.search("fc_network\s?[:=]\s?'?[0-9]+.[0-9]+.[0-9]+", content)
                    framework = "android: fc_network"
                    min_version = Version('0.0.1')
                if match:
                    android_match = match
                    break
            if android_match:
                sp = '=' if '=' in android_match.group(0) else ':'
                version = Version(android_match.group(0).split(sp)[1]
                                  .replace('"', '')
                                  .replace("'", '')
                                  .replace('^', '')
                                  .strip())
            elif len(gradles) > 0:
                (passed, msg) = False, '没有找到 TraceId 暴露的库，使用 rx 请引用 rxvm2 0.4.5 以上版本, 不使用 rx 请引用 ' \
                                       'fc_network 0.0.1 以上版本'
            else:
                print('>> 没有找到安卓配置文件，开始查找 iOS *.podspec 文件')
                _paths = [p for p in glob.glob(str(project_path) + "/**/*.podspec", recursive=True)]
                if len(_paths) <= 0:
                    print('>> 未找到 .podspec 文件，开始查找 Podfile 文件')
                    _paths = [p for p in glob.glob(str(project_path) + "/**/Podfile", recursive=True)]
                    if len(_paths) > 0:
                        with open(_paths[0]) as f:
                            content = f.read()
                        match = re.search("pod 'SCCSwiftyNetwork',\s?'[0-9]+.[0-9]+.[0-9]+", content)
                        min_version = Version('4.1.4')
                        framework = "swift: SCCSwiftyNetwork"
                        if not match:
                            match = re.search("pod 'DFCNetwork',\s?'[0-9]+.[0-9]+.[0-9]+", content)
                            min_version = Version('2.2.12')
                            framework = "ObjC: DFCNetwork"
                        if match:
                            if len(match.group(0).split(':')) < 2:
                                (passed, msg) = True, '库: %s 无定义版本号' % framework
                            else:
                                version = Version(match.group(0).split(':')[1].replace("'", '').strip())
                        else:
                            (passed, msg) = False, '没有找到 TraceId 暴露的库，swift 请引用 SCCSwiftyNetwork 4.1.4 以上版本, ObjC 请引用 ' \
                                                   'DFCNetwork 2.2.12 以上版本'
                else:
                    print('>> 找到 .podspec 文件，当前工程为模块功能')
                    with open(_paths[0]) as f:
                        content = f.read()
                    match = re.search(".dependency 'SCCSwiftyNetwork',\s?'[0-9]+.[0-9]+.[0-9]+0", content)
                    min_version = Version('4.1.4')
                    framework = "swift: SCCSwiftyNetwork"
                    if not match:
                        match = re.search("pod 'DFCNetwork',\s?'[0-9]+.[0-9]+.[0-9]+", content)
                        min_version = Version('2.2.12')
                        framework = "ObjC: DFCNetwork"
                    if match:
                        if len(match.group(0).split(',')) < 2:
                            (passed, msg) = True, '库: %s 无定义版本号，以主工程版本为准' % framework
                        else:
                            version = Version(match.group(0).split(',')[1].replace("'", '').strip())
                    else:
                        (passed, msg) = True, '没有找到网路库的依赖，以主工程版本为准'
        if version:
            if version.equal_or_higher_than(min_version):
                (passed, msg) = True, "当前库: => %s 的版本号 => %s 大于等于支持 traceid 所需的最低版本号 => %s" % (
                    framework, version, min_version)
            else:
                (passed, msg) = False, "当前库: => %s 的版本号 => %s 小于支持 traceid 所需的最低版本号 => %s" % (
                    framework, version, min_version)
        elif not msg:
            msg = '没有找到 H5 RN iOS Android 的配置文件，请检查工程配置是否正确'

        os.system('rm -rf %s' % str(project_path))
        return passed, msg

    @staticmethod
    def lint_git(git, branch):
        project_path = Path.home().joinpath('project4trackid')
        os.system('git clone %s -b %s %s' % (git, branch, str(project_path)))
        return TraceidLinter.lint_path(project_path)

    @staticmethod
    def lint_group(group, name, psw, format):
        gitlab_path = Path.home().joinpath('.dust', '.gitlab')
        gl = Gitlab('https://git.souche-inc.com', email=name, password=psw, api_version='4')
        try:
            gl.auth()
            if not gitlab_path.exists():
                cache = shell.Prompt("是否让 dust 帮你保存帐号密码，以便下次使用(y/n)", default='y').input
                if cache == 'y':
                    with open(str(gitlab_path), 'w+') as f:
                        f.write(json.dumps({'name': name, 'psw': psw}))
        except:
            print('登录失败，请检查用户名或密码')

        search = gl.groups.list(search=group, per_page=100)
        if len(search) <= 0:
            print('未找到该 group ，请确认你有这个 group 的权限')
            return

        if len(search) > 1:
            group_choose = shell.Prompt(
                "找到多个匹配的 group，请选择你想要的 group",
                options=[group.name for group in search],
                numbered=True,
            ).input
            g = [group for group in search if group.name == group_choose][0]
        else:
            g = search[0]

        projects = g.projects.list(per_page=100)
        results = [
            {'name': project.name_with_namespace, 'result': TraceidLinter.lint_git(project.http_url_to_repo, 'master')}
            for project in projects]
        if format == 'html':
            save_path = TraceidLinter.gen_html_report(results, g.name)
        else:
            save_path = TraceidLinter.gen_json_report(results)
        return save_path

    @staticmethod
    def gen_json_report(results):
        save_path = Path.home().joinpath('.dust', 'traceid.json')
        report = [{'name': project['name'],
                   'passed': project['result'][0],
                   'remark': project['result'][1]}
                  for project in results]
        with open(str(save_path), 'w+') as f:
            f.write(json.dumps(report))
        return save_path

    @staticmethod
    def gen_html_report(results, group):
        tr = "<tr><td>%s</td><td>%s</td><td>%s</td></tr>"
        report = '\n'.join([tr % (project['name'], project['result'][0], project['result'][1]) for project in results])
        html = """
<html>
  <head>
      <meta charset="utf-8"> 
      <title>TraceId Report For {group}</title>
      <style>
        table {{
            border-spacing: 0;
            width: 100%;
            border: 1px solid #ddd;
        }}

        th, td {{
            text-align: left;
            padding: 16px;
        }}

        tr:nth-child(even) {{
            background-color: #f2f2f2
        }}
    </style>
  </head>
  <body>
    <table>
      <tr>
        <th>项目名称</th>
        <th onclick="sortTable()">是否支持 traceId</th>
        <th>备注</th>
      </tr>
      {report}
    </table>
    <script>
        function sortTable() {{
          var table, rows, switching, i, x, y, shouldSwitch;
          table = document.getElementById("myTable");
          switching = true;
          while (switching) {{
            switching = false;
            rows = table.getElementsByTagName("TR");
            for (i = 1; i < (rows.length - 1); i++) {{
              shouldSwitch = false;
              x = rows[i].getElementsByTagName("TD")[0];
              y = rows[i + 1].getElementsByTagName("TD")[0];
              if (x.innerHTML.toLowerCase() > y.innerHTML.toLowerCase()) {{
                shouldSwitch = true;
                break;
              }}
            }}
            if (shouldSwitch) {{
              rows[i].parentNode.insertBefore(rows[i + 1], rows[i]);
              switching = true;
            }}
          }}
        }}
    </script>
  </body>
</html>
        """.format(group=group, report=report)
        save_path = Path.home().joinpath('.dust', 'traceid.html')
        with open(str(save_path), 'w+') as f:
            f.write(html)
        return save_path
