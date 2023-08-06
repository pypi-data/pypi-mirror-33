from setuptools import setup, find_packages

setup(
    name='dubi',
    version='1.1.3',
    keywords=('pip', 'dubbo', 'invoke', 'zcy'),
    description='dubbo invoke tool',
    long_description='A tool to invoke dubbo service in zcy',
    license='MIT Licence',
    url='https://github.com/Thare-Lam/dubi.git',
    author='Thare',
    author_email='thare.liang@gmail.com',
    packages=find_packages(),
    exclude_package_data={'': ['*.pyc']},
    platforms='any',
    install_requires=['bs4', 'requests', 'pexpect', 'prettytable'],
    entry_points={
        'console_scripts': ['dubi=dubi.__main__:main']
    }
)
