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
    name='reahl-sqlalchemysupport',
    version='4.0.2',
    description='Support for using SqlAlchemy with Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis package contains infrastructure necessary to use Reahl with SqlAlchemy or Elixir.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.sqlalchemysupport', 'reahl.sqlalchemysupport_dev'],
    py_modules=[],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-component>=4.0,<4.1', 'reahl-commands>=4.0,<4.1', 'sqlalchemy>=1.2.0,<1.2.999', 'alembic>=0.9.6,<0.9.999'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-sqlitesupport>=4.0,<4.1', 'reahl-domain>=4.0,<4.1', 'reahl-dev>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1'],
    test_suite='reahl.sqlalchemysupport_dev',
    entry_points={
        'reahl.persistlist': [
            '0 = reahl.sqlalchemysupport:SchemaVersion'    ],
        'reahl.migratelist': [
            '0 = reahl.sqlalchemysupport.elixirmigration:ElixirToDeclarativeSqlAlchemySupportChanges'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.configspec': [
            'config = reahl.sqlalchemysupport:SqlAlchemyConfig'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
