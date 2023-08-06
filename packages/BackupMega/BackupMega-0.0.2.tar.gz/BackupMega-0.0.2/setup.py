from os.path import join, dirname

from setuptools import find_packages

try:
    from setuptools.core import setup
except ImportError:
    from distutils.core import setup

setup(
    name='BackupMega',
    version='0.0.2',
    author='Nurlan Melis (NMelis)',
    author_email='melis.zhoroev@gmail.com',
    packages=find_packages(),
    url='https://github.com/ProgMeli/backup-mega',
    license='LICENSE.txt',
    description='Backup system and push backup zip to storage mega.nz.',
    long_description=open(join(dirname(__file__), 'README')).read(),
    entry_points={
        'console_scripts':
            ['backup = backup.main:backup']
        },
)
