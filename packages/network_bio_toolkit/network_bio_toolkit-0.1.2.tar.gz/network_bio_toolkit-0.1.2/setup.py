from setuptools import setup

setup(
    name = "network_bio_toolkit",
    packages = ["network_bio_toolkit"],
    version = "0.1.2",
    description = "Network Analysis Toolkit",
    long_description = "network_bio_toolkit provides functions to perform three start-to-finish network analysis workflows: Upstream regulator analysis, heat propagation and clustering network analysis, and gene set enrichment analysis.",
    url = "https://github.com/ucsd-ccbb/network_bio_toolkit",
    author = "Mikayla Webster (13webstermj@gmail.com), Mengyi (Miko) Liu (mikoliu798@gmail.com), Brin Rosenthal (sbrosenthal@ucsd.edu)",
    author_email = "sbrosenthal@ucsd.edu",
    keywords = ['Jupyter notebook', 'interactive', 'network'],
    license = 'MIT',
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2',
    ]
)
