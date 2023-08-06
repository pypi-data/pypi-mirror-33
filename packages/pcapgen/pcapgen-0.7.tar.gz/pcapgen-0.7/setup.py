from setuptools import setup


with open("README.md", "r") as fh:
    long_description = fh.read()


setup(
    name="pcapgen",
    version="0.7",
    author="Sujit Ghosal",
    author_email="synack@outlook.com",
    description=("Module to generate PCAPs from any input file. "
                 "This is a modified version of PGT tool which was"
                 "developed earlier by, Andrewg Felinemenace."),
    license="BSD",
    classifiers=[
        "Environment :: Console",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 2.7",
        "Development Status :: 4 - Beta",
        "Topic :: Utilities",
        "Topic :: Internet",
        "Topic :: System :: Networking",
        "Intended Audience :: Developers"
    ],
    keywords="pcapgen pcap wireshark pgt http imap smtp ftp protocol",
    url="https://pypi.org/project/python-pcapgen/",
    packages=['pcapgen'],
    long_description=long_description,
    long_description_content_type="text/markdown",
    install_requires=[
        'python-magic>=0.4.15',
        'scapy>=2.4.0'
    ],
    dependency_links=[
        'https://pypi.org/project/python-magic/',
        'https://pypi.org/project/scapy/'
    ],
    zip_safe=False
)
