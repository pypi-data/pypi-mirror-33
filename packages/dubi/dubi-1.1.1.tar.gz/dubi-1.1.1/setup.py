from setuptools import setup, find_packages

setup(
    name='dubi',
    version='1.1.1',
    keywords='dubbo invoke',
    description='dubbo invoke tool',
    long_description='A tool to invoke dubbo service',
    license='MIT Licence',
    url='https://github.com/Thare-Lam/dubi',
    author='Thare',
    author_email='thare.liang@gmail.com',
    packages=find_packages(),
    include_package_data=True,
    platforms='any',
    install_requires=['bs4', 'requests', 'pexpect', 'prettytable'],
    entry_points={
        'console_scripts': [
            'dubi = dubi.__main__:main'
        ]
    }
)
