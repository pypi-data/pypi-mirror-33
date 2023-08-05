from setuptools import find_packages, setup

setup(
    name="samur",
    version="0.3.5",
    author="Caner Durmusoglu",
    author_email="cnr437@gmail.com",
    include_package_data=True,
    packages=find_packages(),
    url="https://github.com/ivmech/samur",
    # license="LICENSE.txt",
    description="Samur MainBoard Python Module",
    # long_description=open("README.md").read(),
    # Dependent packages (distributions)
    install_requires=["RPi.GPIO","smbus2"],
)
