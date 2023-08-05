from setuptools import setup

setup(
    name = "ocx_client",
    version = "0.1.1",
    description = "a client library for the bitcoin exchange OCX",
    url = 'https://github.com/ocxapi/ocx-openapi-ruby-client',
    long_description = open("README.md").read(),
    author = "nju520",
    license = "LGPL",
    keywords = "bitcoin ocx ocx.com",
    test_suite = "tests",
    packages = [
        "ocx_client"
    ],
    install_requires = [
        "requests"
    ],
    zip_safe = False
)
