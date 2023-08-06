import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="pcapgen",
    version="0.4",
    author="Sujit Ghosal",
    author_email="synack@outlook.com",
    description="Generate PCAPs by simulating HTTP/FTP/SMTP/IMAP. "
                "A modified version of PGT tools.",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://pypi.org/project/pcapgen/",
    packages=setuptools.find_packages(),
    classifiers=("Operating System :: MacOS :: MacOS X",
                 "Operating System :: Microsoft :: Windows",
                 "Operating System :: POSIX :: Linux",
                 "Programming Language :: Python :: 2.7",
                 "Development Status :: 4 - Beta", "Topic :: Utilities",
                 "Environment :: Console",
                 "Topic :: Internet", "Topic :: System :: Networking",
                 "Intended Audience :: Developers"),
    keywords="pcapgen pcap wireshark pgt pgtlib pft pcapfix",
    install_requires=[
        'python-magic>=0.4.15',
    ],
    dependency_links=['https://pypi.org/project/python-magic/'],
    zip_safe=False)
