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
    name='reahl-web',
    version='4.0.2',
    description='The core Reahl web framework',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis package contains the core of the Reahl framework.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.messages', 'reahl.web', 'reahl.web.bootstrap', 'reahl.web.holder', 'reahl.web.static', 'reahl.web.static.jquery', 'reahl.web_dev', 'reahl.web_dev.advanced', 'reahl.web_dev.advanced.subresources', 'reahl.web_dev.appstructure', 'reahl.web_dev.bootstrap', 'reahl.web_dev.inputandvalidation', 'reahl.web_dev.widgets'],
    py_modules=[],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['reahl-component>=4.0,<4.1', 'ply>=3.8,<3.8.999', 'slimit>=0.8,<0.8.999', 'cssmin>=0.2,<0.2.999', 'BeautifulSoup4>=4.6,<4.6.999', 'webob>=1.4,<1.4.999', 'Babel>=2.1,<2.1.999', 'setuptools>=32.3.1', 'lxml>=4.2,<4.2.999'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1', 'reahl-sqlalchemysupport>=4.0,<4.1', 'reahl-postgresqlsupport>=4.0,<4.1', 'reahl-web-declarative>=4.0,<4.1', 'reahl-domain>=4.0,<4.1', 'reahl-webdev>=4.0,<4.1', 'reahl-mailutil>=4.0,<4.1', 'reahl-dev>=4.0,<4.1'],
    test_suite='reahl.web_dev',
    entry_points={
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.translations': [
            'reahl-web = reahl.messages'    ],
        'reahl.configspec': [
            'config = reahl.web.egg:WebConfig'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
