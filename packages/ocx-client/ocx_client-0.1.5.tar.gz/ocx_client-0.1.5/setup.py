from setuptools import setup

setup(
    name = "ocx_client",
    version = "0.1.5",
    description = "a client library for the bitcoin exchange OCX",
    url = 'https://github.com/ocxapi/ocx-openapi-python-client',
    long_description = open("README.md").read(),
    author = "nju520",
    author_email = 'hwbnju@gmail.com',
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
