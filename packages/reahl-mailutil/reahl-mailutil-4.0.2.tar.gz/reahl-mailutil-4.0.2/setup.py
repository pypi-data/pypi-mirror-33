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
    name='reahl-mailutil',
    version='4.0.2',
    description='Simple utilities for sending email from Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-mailutil is a simple library for sending emails (optionally from ReST sources).\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.mailutil', 'reahl.mailutil_dev'],
    py_modules=[],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-component>=4.0,<4.1', 'docutils>=0.12,<0.12.999', 'Pygments>=2.1.0,<2.1.999'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-dev>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1'],
    test_suite='reahl.mailutil_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.configspec': [
            'config = reahl.mailutil.reusableconfig:MailConfig'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
