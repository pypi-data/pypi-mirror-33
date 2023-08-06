from setuptools import setup, Extension
from setuptools.command.install import install
from setuptools.command.sdist import sdist

import subprocess
import sys

def get_version():
    version = subprocess.check_output(['./genversion.sh', '--print-only'])
    if version.startswith('v'):
        version = version[1:]
    version = version.split('-')[0]
    return version + '.3'    

def get_version_from_file():
    try:
        f = open('./bindings/python/VERSION')
        version = f.read().split('/n')[0]
        f.close()
        return version
    except:
        print('Failed to get version from file. Using unknown')
        return 'unknown'


class CustomInstall(install):
    def run(self): 
        subprocess.call('./install.sh')


class CustomDist(sdist):
    def write_version_to_file(self):
        version = get_version()
        print('WRITING')
        with open('bindings/python/VERSION', 'w') as vi:
            vi.write(version)
    
    def run(self):
        self.write_version_to_file()
        sdist.run(self)


version = get_version()
if version.startswith('unknown'):
    version = get_version_from_file()

setup( 
    name             = 'kjpyxrootd',
    version          = version,
    author           = 'XRootD Developers',
    author_email     = 'xrootd-dev@slac.stanford.edu',
    url              = 'http://xrootd.org',
    license          = 'LGPLv3+',
    description      = "XRootD with Python bindings",
    long_description = "XRootD with Python bindings",
    cmdclass        = {
        'install': CustomInstall,
        'sdist': CustomDist
    }
)
