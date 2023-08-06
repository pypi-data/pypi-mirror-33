import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="echelon_client_agent",
    version="0.0.5",
    author="Inka-labs",
    author_email="eduardo@inka-labs.com",
    description="Communication Agent",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://bitbucket.org/connecttix/echelon-client",
    packages=setuptools.find_packages(),
    include_package_data=True,
    install_requires=[
        "attrs==17.4.0",
        "Automat==0.6.0",
        "certifi==2018.4.16",
        "chardet==3.0.4",
        "constantly==15.1.0",
        "dicttoxml==1.7.4",
        "hyperlink==18.0.0",
        "idna==2.6",
        "incremental==17.5.0",
        "pytz==2017.3",
        "requests==2.18.4",
        "six==1.11.0",
        "SQLAlchemy==1.2.1",
        "Twisted==18.4.0",
        "urllib3==1.22",
        "zope.interface==4.5.0",
    ],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)
