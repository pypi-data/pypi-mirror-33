from setuptools import setup, find_packages
from dubi.info import *

setup(
    name='dubi',
    version=version,
    keywords=('pip', 'dubbo', 'invoke', 'zcy'),
    description=description,
    long_description='A tool to invoke dubbo service in zcy',
    license='MIT Licence',
    url=source,
    author='Thare',
    author_email=email,
    packages=find_packages(),
    exclude_package_data={'': ['*.pyc']},
    platforms='any',
    install_requires=['bs4', 'requests', 'pexpect', 'prettytable'],
    entry_points={
        'console_scripts': ['dubi=dubi.__main__:main']
    }
)
