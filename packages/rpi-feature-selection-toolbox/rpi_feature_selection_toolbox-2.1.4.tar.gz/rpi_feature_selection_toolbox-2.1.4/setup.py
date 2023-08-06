import os
from setuptools import setup
from setuptools.command.develop import develop
from setuptools.command.install import install
from urllib import request
#import zipfile

HOME = "/opt/mcr/"

ELEM = ["v94/runtime/glnxa64", 
        "v94/bin/glnxa64", 
        "v94/sys/os/glnxa64"
        ]

class PostDevelopCommand(develop):
    """Post-installation for development mode."""
    def run(self):
        if not os.path.exists(HOME):
            os.makedirs(HOME)
        path_found = 0
        for elem in ELEM:
            fname = os.path.join(HOME, elem)
            if (os.path.exists(fname)):
                path_found = 1
                break
        if path_found == 0:
            url = "http://ssd.mathworks.com/supportfiles/downloads/R2018a/deployment_files/R2018a/installers/glnxa64/MCR_R2018a_glnxa64_installer.zip"
            request.urlretrieve(url, "/usr/src/MCR_installer.zip")
            os.system("unzip /usr/src/MCR_installer.zip -d /usr/src") #unzip the files to folder /usr/src
            os.system("/usr/src/install -mode silent -agreeToLicense yes -destinationFolder /opt/mcr")
            #os.system("echo /opt/mcr/v94/runtime/glnxa64 > /etc/ld.so.conf.d/zzz-matlab.conf")
            #os.system("echo /opt/mcr/v94/bin/glnxa64 >> /etc/ld.so.conf.d/zzz-matlab.conf")
            #os.system("echo /opt/mcr/v94/sys/os/glnxa64 >> /etc/ld.so.conf.d/zzz-matlab.conf")
            #os.system("ldconfig")
            os.system("rm -rf /usr/src/*")
        develop.run(self)

class PostInstallCommand(install):
    """Post-installation for installation mode."""
    def run(self):
        if not os.path.exists(HOME):
            os.makedirs(HOME)
        path_found = 0
        for elem in ELEM:
            fname = os.path.join(HOME, elem)
            if (os.path.exists(fname)):
                path_found = 1
                break
        if path_found == 0:
            url = "http://ssd.mathworks.com/supportfiles/downloads/R2018a/deployment_files/R2018a/installers/glnxa64/MCR_R2018a_glnxa64_installer.zip"
            request.urlretrieve(url, "/usr/src/MCR_installer.zip")
            os.system("unzip /usr/src/MCR_installer.zip -d /usr/src")
            os.system("/usr/src/install -mode silent -agreeToLicense yes -destinationFolder /opt/mcr")
            #os.system("echo /opt/mcr/v94/runtime/glnxa64 > /etc/ld.so.conf.d/zzz-matlab.conf")
            #os.system("echo /opt/mcr/v94/bin/glnxa64 >> /etc/ld.so.conf.d/zzz-matlab.conf")
            #os.system("echo /opt/mcr/v94/sys/os/glnxa64 >> /etc/ld.so.conf.d/zzz-matlab.conf")
            #os.system("ldconfig")
            os.system("rm -rf /usr/src/*")       
        install.run(self)

setup(
	name='rpi_feature_selection_toolbox',  # This is the name of your PyPI-package. 
	version= '2.1.4',  # Update the version number for new releases
	author='Keyi Liu, Zijun Cui, Qiang Ji',
	#packages = find_packages(exclude=['contrib', 'docs', 'tests*']),
    install_requires = [
            'd3m'
            #'d3m_metadata',
            #'primitive_interfaces',
            #'matlab'
            ],
	url='https://www.ecse.rpi.edu/~cvrl/',
	description='RPI primitives using the latest 2018.6 APIs',
	platforms=['Linux', 'MacOS'],
	packages=['rpi_feature_selection_toolbox'],
        package_data={'rpi_feature_selection_toolbox':['*.ctf']},
   cmdclass = {
            'develop':PostDevelopCommand,
            'install':PostInstallCommand,
            },
    
)
