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
    name='reahl-domain',
    version='4.0.2',
    description='End-user domain functionality for use with Reahl.',
    long_description='Reahl is a web application framework that allows a Python programmer to work in terms of useful abstractions - using a single programming language.\n\nThis Reahl component includes functionality modelling user accounts, some simple workflow concepts and more.\n\nSee http://www.reahl.org/docs/4.0/tutorial/gettingstarted-install.d.html for installation instructions. ',
    url='http://www.reahl.org',
    maintainer='Iwan Vosloo',
    maintainer_email='iwan@reahl.org',
    packages=['reahl', 'reahl.domain', 'reahl.domain_dev', 'reahl.messages'],
    py_modules=[],
    include_package_data=True,
    package_data={'': ['*/LC_MESSAGES/*.mo']},
    namespace_packages=['reahl', 'reahl.messages'],
    install_requires=['passlib>=1.7.1,<1.7.9999', 'reahl-component>=4.0,<4.1', 'reahl-mailutil>=4.0,<4.1', 'reahl-sqlalchemysupport>=4.0,<4.1', 'reahl-web-declarative>=4.0,<4.1'],
    setup_requires=['setuptools-git>=1.1,<1.1.999', 'pytest-runner'],
    tests_require=['pytest>=3.0', 'reahl-tofu>=4.0,<4.1', 'reahl-stubble>=4.0,<4.1', 'reahl-dev>=4.0,<4.1', 'reahl-postgresqlsupport>=4.0,<4.1', 'reahl-webdev>=4.0,<4.1'],
    test_suite='reahl.domain_dev',
    entry_points={
        'reahl.persistlist': [
            '0 = reahl.partymodel:Party',
            '1 = reahl.systemaccountmodel:SystemAccount',
            '2 = reahl.systemaccountmodel:LoginSession',
            '3 = reahl.systemaccountmodel:EmailAndPasswordSystemAccount',
            '4 = reahl.systemaccountmodel:AccountManagementInterface',
            '5 = reahl.systemaccountmodel:VerificationRequest',
            '6 = reahl.systemaccountmodel:VerifyEmailRequest',
            '7 = reahl.systemaccountmodel:NewPasswordRequest',
            '8 = reahl.systemaccountmodel:ActivateAccount',
            '9 = reahl.systemaccountmodel:ChangeAccountEmail',
            '10 = reahl.workflowmodel:DeferredAction',
            '11 = reahl.workflowmodel:Requirement',
            '12 = reahl.workflowmodel:Queue',
            '13 = reahl.workflowmodel:Task'    ],
        'reahl.configspec': [
            'config = reahl.systemaccountmodel:SystemAccountConfig'    ],
        'reahl.eggs': [
            'Egg = reahl.component.eggs:ReahlEgg'    ],
        'reahl.migratelist': [
            '0 = reahl.domain.migrations:ElixirToDeclarativeDomainChanges',
            '1 = reahl.domain.migrations:AddLoginSession',
            '2 = reahl.domain.migrations:ChangeSchemaToBeMySqlCompatible',
            '3 = reahl.domain.migrations:ChangePasswordHash',
            '4 = reahl.domain.migrations:RemoveDeadApacheDigestColumn'    ],
        'reahl.translations': [
            'reahl-domain = reahl.messages'    ],
        'reahl.scheduled_jobs': [
            'reahl.workflowmodel:DeferredAction.check_deadline = reahl.workflowmodel:DeferredAction.check_deadline'    ],
                 },
    extras_require={},
    cmdclass={'install_test_dependencies': InstallTestDependencies}
)
