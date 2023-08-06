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
    name='reahl-domainui',
    version='4.0.2',
    description='A user interface for reahl-domain.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis Reahl component contains a user interface for some of the domain functionality in reahl-domainui.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.domainui', 'reahl.domainui.bootstrap', 'reahl.domainui_dev', 'reahl.domainui_dev.bootstrap', 'reahl.messages'],
    py_modules=[],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['reahl-component>=4.0,<4.1', 'reahl-sqlalchemysupport>=4.0,<4.1', 'reahl-web>=4.0,<4.1', 'reahl-web-declarative>=4.0,<4.1', 'reahl-domain>=4.0,<4.1', 'setuptools>=32.3.1'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1', 'reahl-dev>=4.0,<4.1', 'reahl-webdev>=4.0,<4.1', 'reahl-postgresqlsupport>=4.0,<4.1'],
    test_suite='reahl.domainui_dev',
    entry_points={
        'reahl.translations': [
            'reahl-domainui = reahl.messages'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.workflowui.task_widgets': [
            'bootstrap.TaskWidget = reahl.domainui.bootstrap.workflow:TaskWidget'    ],
        'reahl.configspec': [
            'config = reahl.domainuiegg:DomainUiConfig'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
