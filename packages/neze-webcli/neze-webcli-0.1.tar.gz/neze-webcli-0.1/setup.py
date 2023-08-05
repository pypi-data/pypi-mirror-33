import setuptools
from webcli.utils.git import versiontag
from webcli import name

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name='neze-webcli',
    version=str(versiontag().version()),
    author="Clement Durand",
    author_email="durand.clement.13@gmail.com",
    description="Utility suite",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
    ),
    entry_points={
        'console_scripts': [
            'transmission = webcli.cli.transmission:main',
            'gitlab = webcli.cli.gitlab:main',
            'git-piptag = webcli.cli.git_piptag:main',
        ]
    },
    install_requires=['requests','PyYAML'],
)
