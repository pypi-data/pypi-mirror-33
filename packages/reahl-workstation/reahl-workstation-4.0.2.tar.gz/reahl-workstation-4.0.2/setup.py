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
    name='reahl-workstation',
    version='4.0.2',
    description='Useful commands to ease development.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-workstation contains a few utilities that helps to have available on a developer workstation.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.workstation', 'reahl.workstation_dev'],
    py_modules=[],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['six', 'reahl-component>=4.0,<4.1'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1', 'reahl-dev>=4.0,<4.1'],
    test_suite='reahl.workstation_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.component.commands': [
            'Xpra = reahl.workstation.xprasupport:ControlXpra',
            'Ngrok = reahl.workstation.ngroksupport:Ngrok'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
