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
    name='reahl-tofu',
    version='4.0.2',
    description='A testing framework that couples fixtures and tests loosely.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nTofu is part of the Reahl development tools. Tofu can be used independently of the Reahl web framework.\n\nTofu allows you to have a hierarchy of test fixtures that is *completely* decoupled from your hierarchy of tests or test suites. Tofu includes a number of other related test utilities. It also includes a plugin for nosetests that makes using it with nose seamless.\n\nTofu can also be used to run the set_ups of fixtures from the command line.  This is useful for acceptance tests whose fixtures create data in databases that can be used for demonstration and user testing. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['devenv', 'examples', 'reahl', 'reahl.tofu', 'reahl.tofu_dev', 'tofu_test'],
    py_modules=[],
    include_package_data=False,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['six', 'wrapt>=1.10.2,<1.10.999', 'reahl-component>=4.0,<4.1'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0'],
    test_suite='reahl.tofu_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
