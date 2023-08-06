
from setuptools import setup, find_packages
from setuptools.command.develop import develop
from setuptools.command.install import install
import sys, os
from DustCli.utils.version import version


class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        develop.run(self)
        os.system('dust init')


class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        install.run(self)
        os.system('dust init')


setup(
    name='DustCli',
    version=version,
    description="dust cli",
    long_description="SCFEE iOS Android 脚手架",
    classifiers=[],
    keywords='',
    author='shaotianchi',
    author_email='shaotianchi@souche.com',
    url='https://tangeche.com',
    license='MIT',
    packages=find_packages(exclude=['ez_setup', 'examples', 'tests']),
    include_package_data=True,
    zip_safe=False,
    test_suite='nose.collector',
    cmdclass={
        'develop': PostDevelopCommand,
        'install': PostInstallCommand,
    },
    install_requires=[
        'cement',
        'pbxproj',
        'colorlog',
        'requests',
        'PyYaml',
        'python-gitlab'
        ],
    setup_requires=[],
    entry_points="""
        [console_scripts]
        dust = DustCli.cli.main:main
    """,
    namespace_packages=[],
    )
