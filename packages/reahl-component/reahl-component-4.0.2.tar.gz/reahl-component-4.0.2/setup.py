from setuptools import setup, Command
class InstallTestDependencies(Command):
    user_options = []
    def run(self):
        import sys
        import subprocess
        if self.distribution.tests_require: subprocess.check_call([sys.executable, "-m", "pip", "install", "-q"]+self.distribution.tests_require)

    def initialize_options(self):
        pass

    def finalize_options(self):
        pass

setup(
    name='reahl-component',
    version='4.0.2',
    description='The component framework of Reahl.',
    long_description="Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-component is the component that contains Reahl's component framework.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ",
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.component', 'reahl.component_dev', 'reahl.messages'],
    py_modules=[],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['six', 'Babel>=2.1,<2.1.999', 'python-dateutil>=2.2,<2.2.999', 'wrapt>=1.10.2,<1.10.999', 'setuptools>=32.3.1', 'pip>=10.0.0'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1', 'reahl-dev>=4.0,<4.1', 'reahl-sqlalchemysupport>=4.0,<4.1', 'reahl-sqlitesupport>=4.0,<4.1', 'reahl-mysqlsupport>=4.0,<4.1'],
    test_suite='reahl.component_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.translations': [
            'reahl-component = reahl.messages'    ],
        'console_scripts': [
            'reahl = reahl.component.shelltools:ReahlCommandline.execute_one'    ],
        'reahl.component.databasecontrols': [
            'NullDatabaseControl = reahl.component.dbutils:NullDatabaseControl'    ],
        'reahl.component.commands': [
            'AddAlias = reahl.component.shelltools:AddAlias',
            'RemoveAlias = reahl.component.shelltools:RemoveAlias'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
