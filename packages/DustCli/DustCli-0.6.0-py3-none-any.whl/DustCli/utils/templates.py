from cement.utils import shell
from pathlib import Path
import shutil
import yaml
from DustCli.utils.git import GitUtil

tempPath = Path.home().joinpath('.dust', 'ProjectTemplates')
customTempPath = Path.home().joinpath('.dust', 'CustomProjectTemplates')
customPluginPath = Path.home().joinpath('.dust', 'CustomPlugins')
pluginPath = Path.home().joinpath('.dust', 'Plugins')


class Func:
    def __init__(self, value):
        self.name = value.split(':')[0]
        self.params = value.split(':')[1:]

    @staticmethod
    def decode(array):
        return [Func(value) for value in array]

    def ios_desc(self, swift):
        if swift and len(self.params) > 0:
            params_str = ', '.join(
                [('<#%s#>' % param, '%s: <#%s#>' % (param, param))[param != '_'] for param in self.params])
            return '%s(%s)' % (self.name, params_str)
        elif swift and len(self.params) <= 0:
            return '%s()' % self.name
        elif not swift and len(self.params) > 0:
            params_str = ' '.join(
                ['<#%s#>' % param if param == '_' else '%s: <#%s#>' % (param, param) for param in self.params])
            return '[self %s:%s];' % (self.name, params_str)
        else:
            return '[self %s];' % self.name


class ProjectPlugin:
    @staticmethod
    def load(platform, lang):
        plugin_path = pluginPath.joinpath(platform, lang, 'plugins.yml')
        if customPluginPath.is_dir():
            plugin_path = customPluginPath.joinpath(platform, lang, 'plugins.yml')
        elif not pluginPath.is_dir():
            ProjectTemplate.clone_if_need()

        if not plugin_path.exists():
            return []

        with open(str(plugin_path), 'r') as stream:
            try:
                plugins = yaml.load(stream)
                return [ProjectPlugin(key, value, platform, lang) for key, value in plugins.items()]
            except yaml.YAMLError as exc:
                print(exc)
                return []

    def __init__(self, name, value, platform, lang):
        self.platform = platform
        self.lang = lang
        self.name = name
        self.desc = value['desc']
        self.code = value['code']
        self.files = value.get('file', [])
        self.pod = value['pod']
        self.imports = value.get('imports', [])
        self.func = Func.decode(value['func'])
        self.need = False

    @property
    def code_path(self):
        return Path.home().joinpath('.dust', 'Plugins', self.platform, self.lang, self.code)

    def file_path(self, filename):
        return Path.home().joinpath('.dust', 'Plugins', self.platform, self.lang, filename)


class ProjectTemplate:

    @staticmethod
    def clone():
        GitUtil.clone('git@git.souche-inc.com:SCFEE/project-template.git', tempPath)
        GitUtil.clone('git@git.souche-inc.com:SCFEE/Plugins-For-Cli.git', pluginPath)

    @staticmethod
    def clone_if_need():
        GitUtil.clone('git@git.souche-inc.com:SCFEE/project-template.git', tempPath)
        GitUtil.clone('git@git.souche-inc.com:SCFEE/Plugins-For-Cli.git', pluginPath)

    @staticmethod
    def clone_custom_template(git):
        GitUtil.clone(git, customTempPath)

    @staticmethod
    def clone_custom_plugins(git):
        GitUtil.clone(git, customPluginPath)

    @staticmethod
    def copy_custom_template(path):
        if Path(customTempPath).is_dir():
            shutil.rmtree(customTempPath)

        shutil.copytree(path, customTempPath)

    @staticmethod
    def clean_custom_template():
        if Path(customTempPath).is_dir():
            shutil.rmtree(customTempPath)

    @staticmethod
    def copy_custom_plugins(path):
        if Path(customPluginPath).is_dir():
            shutil.rmtree(customPluginPath)

        shutil.copytree(path, customPluginPath)

    @staticmethod
    def clean_custom_plugins():
        if Path(customPluginPath).is_dir():
            shutil.rmtree(customPluginPath)
