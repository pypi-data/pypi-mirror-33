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
    name='reahl-webdev',
    version='4.0.2',
    description='Web-specific development tools for Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl development tools for testing and working with web based programs.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.webdev', 'reahl.webdev_dev'],
    py_modules=[],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-web>=4.0,<4.1', 'reahl-dev>=4.0,<4.1', 'reahl-component>=4.0,<4.1', 'reahl-tofu>=4.0,<4.1', 'reahl-domain>=4.0,<4.1', 'lxml>=4.2,<4.2.999', 'WebTest>=2.0,<2.0.999', 'selenium>=2.42,<2.9999', 'watchdog>=0.8.3,<0.8.999.3', 'setuptools>=32.3.1', 'webob>=1.4,<1.4.999'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-postgresqlsupport>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1'],
    test_suite='reahl.webdev_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.component.commands': [
            'ServeCurrentProject = reahl.webdev.commands:ServeCurrentProject',
            'SyncFiles = reahl.webdev.commands:SyncFiles'    ],
                 },
    extras_require={'pillow': ['pillow>=2.5,<2.5.999']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
