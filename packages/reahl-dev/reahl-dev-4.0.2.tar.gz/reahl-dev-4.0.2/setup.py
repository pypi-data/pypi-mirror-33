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
    name='reahl-dev',
    version='4.0.2',
    description='The core Reahl development tools.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-dev is the component containing general Reahl development tools.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.dev', 'reahl.dev_dev'],
    py_modules=[],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-component>=4.0,<4.1', 'reahl-tofu>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1', 'six', 'Babel>=2.1,<2.1.999', 'twine>=1.11.0,<1.11.9999', 'wheel>=0.29.0,<0.29.9999', 'tzlocal>=1.2.0,<1.2.9999', 'setuptools>=32.3.1', 'pip>=10.0.0'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0'],
    test_suite='reahl.dev_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.component.commands': [
            'Refresh = reahl.dev.devshell:Refresh',
            'ExplainLegend = reahl.dev.devshell:ExplainLegend',
            'List = reahl.dev.devshell:List',
            'Select = reahl.dev.devshell:Select',
            'ClearSelection = reahl.dev.devshell:ClearSelection',
            'ListSelections = reahl.dev.devshell:ListSelections',
            'Save = reahl.dev.devshell:Save',
            'Read = reahl.dev.devshell:Read',
            'DeleteSelection = reahl.dev.devshell:DeleteSelection',
            'Shell = reahl.dev.devshell:Shell',
            'Setup = reahl.dev.devshell:Setup',
            'Build = reahl.dev.devshell:Build',
            'ListMissingDependencies = reahl.dev.devshell:ListMissingDependencies',
            'DebInstall = reahl.dev.devshell:DebInstall',
            'Upload = reahl.dev.devshell:Upload',
            'MarkReleased = reahl.dev.devshell:MarkReleased',
            'SubstVars = reahl.dev.devshell:SubstVars',
            'Debianise = reahl.dev.devshell:Debianise',
            'Info = reahl.dev.devshell:Info',
            'ExtractMessages = reahl.dev.devshell:ExtractMessages',
            'MergeTranslations = reahl.dev.devshell:MergeTranslations',
            'CompileTranslations = reahl.dev.devshell:CompileTranslations',
            'AddLocale = reahl.dev.devshell:AddLocale',
            'UpdateAptRepository = reahl.dev.devshell:UpdateAptRepository',
            'ServeSMTP = reahl.dev.mailtest:ServeSMTP',
            'UpdateCopyright = reahl.dev.devshell:UpdateCopyright'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
