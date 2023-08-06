from setuptools import setup

setup(
    name='impersonator',
    version='0.1.0',
    description='A Python client for the Impersonator service',
    url='https://github.com/Stavatech/Impersonator-Python-Client',
    author='David Brown',
    author_email='davidbrownza@outlook.com',
    license='GPLv3',
    packages=['impersonator'],
    install_requires=[
        'requests',
        'mock'
    ],
    zip_safe=False
)