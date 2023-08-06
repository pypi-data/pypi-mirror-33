# encoding: utf-8

from setuptools import setup, find_packages

setup(
    name="gsenha",
    version="0.0.5",
    description="client for gsenha api",
    author="Big Data",
    author_email="bigdata@corp.globo.com",
    license='MIT',
    install_requires=[
        "asn1crypto==0.22.0",
        "certifi==2017.4.17",
        "cffi==1.10.0",
        "chardet==3.0.4",
        "cryptography==1.9",
        "enum34==1.1.6",
        "idna==2.5",
        "ipaddress==1.0.18",
        "pycparser==2.18",
        "requests==2.18.1",
        "six==1.10.0",
        "urllib3==1.21.1"
    ],
    packages=find_packages(),
)
