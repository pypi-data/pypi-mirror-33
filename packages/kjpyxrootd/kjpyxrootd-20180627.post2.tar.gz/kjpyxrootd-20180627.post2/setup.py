from setuptools import setup, Extension
from setuptools.command.install import install

import subprocess
import sys


class CustomInstall(install):
    def run(self): 
        subprocess.call('./install.sh')


def get_version():
    version = subprocess.check_output(['./genversion.sh', '--print-only'])
    if version.startswith('v'):
        version = version[1:]
    version = version.split('-')[0]
    return version + '-2'

version = get_version()

with open('bindings/python/VERSION_INFO', 'w') as vi:
    vi.write(version)


setup( 
    name             = 'kjpyxrootd',
    version          = version,
    author           = 'XRootD Developers',
    author_email     = 'xrootd-dev@slac.stanford.edu',
    url              = 'http://xrootd.org',
    license          = 'LGPLv3+',
    description      = "XRootD with Python bindings",
    long_description = "XRootD with Python bindings",
    cmdclass        = {'install': CustomInstall}
)
