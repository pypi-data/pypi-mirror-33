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
    name='reahl-doc',
    version='4.0.2',
    description='Documentation and examples for Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nReahl-doc contains documentation and examples of Reahl.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.doc', 'reahl.doc.examples', 'reahl.doc.examples.tutorial', 'reahl.doc.examples.tutorial.accessbootstrap', 'reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap_dev', 'reahl.doc.examples.tutorial.addressbook1', 'reahl.doc.examples.tutorial.addressbook1.addressbook1_dev', 'reahl.doc.examples.tutorial.addressbook2', 'reahl.doc.examples.tutorial.addressbook2.addressbook2_dev', 'reahl.doc.examples.tutorial.addressbook2bootstrap', 'reahl.doc.examples.tutorial.addressbook2bootstrap.addressbook2bootstrap_dev', 'reahl.doc.examples.tutorial.addresslist', 'reahl.doc.examples.tutorial.ajaxbootstrap', 'reahl.doc.examples.tutorial.ajaxbootstrap.ajaxbootstrap_dev', 'reahl.doc.examples.tutorial.bootstrapgrids', 'reahl.doc.examples.tutorial.componentconfigbootstrap', 'reahl.doc.examples.tutorial.componentconfigbootstrap.componentconfigbootstrap_dev', 'reahl.doc.examples.tutorial.datatablebootstrap', 'reahl.doc.examples.tutorial.datatablebootstrap.datatablebootstrap_dev', 'reahl.doc.examples.tutorial.hello', 'reahl.doc.examples.tutorial.helloanywhere', 'reahl.doc.examples.tutorial.helloapache', 'reahl.doc.examples.tutorial.hellonginx', 'reahl.doc.examples.tutorial.i18nexamplebootstrap', 'reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrap_dev', 'reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrapmessages', 'reahl.doc.examples.tutorial.jobsbootstrap', 'reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap_dev', 'reahl.doc.examples.tutorial.login1bootstrap', 'reahl.doc.examples.tutorial.login1bootstrap.login1bootstrap_dev', 'reahl.doc.examples.tutorial.login2bootstrap', 'reahl.doc.examples.tutorial.login2bootstrap.login2bootstrap_dev', 'reahl.doc.examples.tutorial.migrationexamplebootstrap', 'reahl.doc.examples.tutorial.migrationexamplebootstrap.migrationexamplebootstrap_dev', 'reahl.doc.examples.tutorial.pageflow1', 'reahl.doc.examples.tutorial.pageflow1.pageflow1_dev', 'reahl.doc.examples.tutorial.pagelayout', 'reahl.doc.examples.tutorial.pagerbootstrap', 'reahl.doc.examples.tutorial.pagerbootstrap.pagerbootstrap_dev', 'reahl.doc.examples.tutorial.parameterised1', 'reahl.doc.examples.tutorial.parameterised2', 'reahl.doc.examples.tutorial.parameterised2.parameterised2_dev', 'reahl.doc.examples.tutorial.sessionscopebootstrap', 'reahl.doc.examples.tutorial.sessionscopebootstrap.sessionscopebootstrap_dev', 'reahl.doc.examples.tutorial.slots', 'reahl.doc.examples.tutorial.tablebootstrap', 'reahl.doc.examples.tutorial.tablebootstrap.etc', 'reahl.doc.examples.tutorial.tablebootstrap.tablebootstrap_dev', 'reahl.doc.examples.web', 'reahl.doc.examples.web.basichtmlinputs', 'reahl.doc.examples.web.basichtmlinputs.basichtmlinputs_dev', 'reahl.doc.examples.web.basichtmlwidgets', 'reahl.doc.examples.web.fileupload', 'reahl.doc_dev'],
    py_modules=[],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl'],
    install_requires=['reahl-web>=4.0,<4.1', 'reahl-component>=4.0,<4.1', 'reahl-sqlalchemysupport>=4.0,<4.1', 'reahl-web-declarative>=4.0,<4.1', 'reahl-domain>=4.0,<4.1', 'reahl-domainui>=4.0,<4.1', 'reahl-commands>=4.0,<4.1', 'pytest>=3.0', 'setuptools>=32.3.1'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'Sphinx', 'reahl-tofu>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1', 'reahl-dev>=4.0,<4.1', 'reahl-webdev>=4.0,<4.1', 'reahl-postgresqlsupport>=4.0,<4.1', 'reahl-sqlitesupport>=4.0,<4.1', 'reahl-mysqlsupport>=4.0,<4.1'],
    test_suite='reahl.doc_dev',
    entry_points={
        'reahl.persistlist': [
            '0 = reahl.doc.examples.web.fileupload.fileupload:Comment',
            '1 = reahl.doc.examples.web.fileupload.fileupload:AttachedFile',
            '2 = reahl.doc.examples.tutorial.addressbook2.addressbook2:Address',
            '3 = reahl.doc.examples.tutorial.addressbook2bootstrap.addressbook2bootstrap:Address',
            '4 = reahl.doc.examples.tutorial.addressbook1.addressbook1:Address',
            '5 = reahl.doc.examples.tutorial.pageflow1.pageflow1:Address',
            '6 = reahl.doc.examples.tutorial.parameterised1.parameterised1:Address',
            '7 = reahl.doc.examples.tutorial.parameterised2.parameterised2:Address',
            '8 = reahl.doc.examples.tutorial.sessionscopebootstrap.sessionscopebootstrap:User',
            '9 = reahl.doc.examples.tutorial.sessionscopebootstrap.sessionscopebootstrap:LoginSession',
            '10 = reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap:AddressBook',
            '11 = reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap:Collaborator',
            '12 = reahl.doc.examples.tutorial.accessbootstrap.accessbootstrap:Address',
            '13 = reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrap:Address',
            '14 = reahl.doc.examples.tutorial.componentconfigbootstrap.componentconfigbootstrap:Address',
            '15 = reahl.doc.examples.tutorial.migrationexamplebootstrap.migrationexamplebootstrap:Address',
            '16 = reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap:Address',
            '17 = reahl.doc.examples.tutorial.tablebootstrap.tablebootstrap:Address',
            '18 = reahl.doc.examples.tutorial.datatablebootstrap.datatablebootstrap:Address'    ],
        'reahl.scheduled_jobs': [
            'reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap:Address.clear_added_flags = reahl.doc.examples.tutorial.jobsbootstrap.jobsbootstrap:Address.clear_added_flags'    ],
        'reahl.configspec': [
            'config = reahl.doc.examples.tutorial.componentconfigbootstrap.componentconfigbootstrap:AddressConfig'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.translations': [
            'reahl-doc = reahl.doc.examples.tutorial.i18nexamplebootstrap.i18nexamplebootstrapmessages'    ],
        'reahl.component.commands': [
            'GetExample = reahl.doc.commands:GetExample',
            'ListExamples = reahl.doc.commands:ListExamples'    ],
                 },
    extras_require={'pillow': ['pillow']},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
