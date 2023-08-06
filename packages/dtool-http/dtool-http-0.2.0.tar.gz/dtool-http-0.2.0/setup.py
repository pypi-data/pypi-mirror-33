from setuptools import setup

url = "https://github.com/jic-dtool/dtool-http"
version = "0.2.0"
readme = open('README.rst').read()

setup(
    name="dtool-http",
    packages=["dtool_http"],
    version=version,
    description="Add HTTP read only dataset support to dtool",
    long_description=readme,
    include_package_data=True,
    # Package will be released using Tjelvar's PyPi credentials.
    author="Tjelvar Olsson",
    author_email="tjelvar.olsson@jic.ac.uk",
#   author="Matthew Hartley",  # NOQA
#   author_email="Matthew.Hartley@jic.ac.uk",  # NOQA
    url=url,
    install_requires=[
        "dtoolcore>=3.0",
        "requests",
    ],
    entry_points={
        "dtool.storage_brokers": [
            "HTTPStorageBroker=dtool_http.storagebroker:HTTPStorageBroker",
            "HTTPSStorageBroker=dtool_http.storagebroker:HTTPSStorageBroker",
        ],
        "console_scripts": [
            "dtool_serve_directory=dtool_http.server:cli",
            "dtool_publish_dataset=dtool_http.publish:cli"
        ]
    },
    download_url="{}/tarball/{}".format(url, version),
    license="MIT"
)
