import os
from setuptools import setup, find_packages
from sieve.sdk import __VERSION__


long_description = open(os.path.join(os.path.dirname(__file__), 'README.md'),
                        encoding='utf-8').read()

setup(
    name='sieve_sdk',
    version=__VERSION__,
    description='Sieve SDK',
    long_description=long_description,
    author='Diogo Magalhaes Martins',
    author_email='diogo.martins@sieve.com.br',
    url='https://bitbucket.org/sievetech/sieve-python-sdk',
    packages=find_packages(exclude=['tests', 's3_upload', 'deploy.sh']),
    install_requires=[
        "aiodns==1.1.1",
        "aiohttp>=3.1.2",
        "aiosocksy==0.1",
        "cchardet==2.1.1",
        "pathdict>=0.0.9",
        "simple_json_logger>=0.2.2"
    ],
    include_package_data=True,
)
