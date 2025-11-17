from setuptools import setup, find_packages

setup(
    name="kumiho",
    version="0.3.0",
    packages=find_packages(),
    install_requires=[
        "grpcio",
        "grpcio-tools",
    ],
    description="Client library for the Kumiho asset management system.",
    license="Apache-2.0",
    classifiers=[
        "License :: OSI Approved :: Apache Software License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3 :: Only",
        "Operating System :: OS Independent",
    ],
)