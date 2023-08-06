from distutils.core import setup
# from setuptools import setup
# from setuptools.command.develop import develop
from setuptools.command.install import install
import subprocess
from subprocess import check_call
import os

# class PostDevelopCommand(develop):
#     """Post-installation for installation mode."""

#     def run(self):
#         print "We are running in the PostDevelopCommand"
#         develop.run(self)


class PostInstallCommand(install):
    """Post-installation for installation mode."""

    def run(self):
        print "We are running in the postInstallCommand"
        cwd = os.path.dirname(os.path.realpath(__file__))
        check_call("bash %s/azure_env.sh" % cwd, shell=True)
        check_call("bash %s/waagent/csr_waagent_install.sh" % cwd, shell=True)
        check_call("bash %s/install_tools.sh %s" % (cwd, project_ver),
                   shell=True)
        install.run(self)


project_name = 'csr_azure_guestshell'
project_ver = '1.1.3'
setup(
    name=project_name,
    packages=[project_name],  # this must be the same as the name above
    version=project_ver,
    description='A helper library for Cisco guestshell on Azure',
    author='Christopher Reder',
    author_email='creder@cisco.com',
    scripts=['csr_azure_guestshell/bin/get-metadata.py',
             'csr_azure_guestshell/bin/save-config-to-storage.py',
             'csr_azure_guestshell/bin/save-tech-support-to-storage.py',
             'csr_azure_guestshell/bin/load-bin-from-storage.py',
             'csr_azure_guestshell/bin/capture-interface.py'],
    # use the URL to the github repo
    url='https://github4-chn.cisco.com/csr1000v-azure/' + project_name,
    download_url='https://github4-chn.cisco.com/csr1000v-azure/' + project_name + '/archive/' + \
        project_ver + '.tar.gz',
    keywords=['cisco', 'azure', 'csr1000v', 'csr', 'guestshell'],
    classifiers=[],
    license="MIT",
    include_package_data=True,
    cmdclass={
        'install': PostInstallCommand,
    },
)
