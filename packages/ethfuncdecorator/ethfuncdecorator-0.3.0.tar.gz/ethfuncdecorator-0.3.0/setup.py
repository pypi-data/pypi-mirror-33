from distutils.core import setup

setup(
    # Application name:
    name="ethfuncdecorator",

    # Version number (initial):
    version="0.3.0",

    # Application author details:
    author="Lyubomir Kiprov",
    author_email="lyubo@limechain.tech",

    # Packages
    packages=["src"],

    # Include additional files into the package
    include_package_data=True,

    #
    # license="LICENSE.txt",
    description="Decorate web3 contract functions to be easily used",

    # long_description=open("README.txt").read(),

    # Dependent packages (distributions)
    # install_requires=[
    #     "web3=4.3.0",
    # ],
)
