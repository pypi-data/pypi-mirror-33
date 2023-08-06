import sys
from setuptools import setup, find_packages

if sys.version_info.major < 2:
    sys.exit("Error: Please upgrade to Python3")


def get_long_description():
    with open("README.rst") as fp:
        return fp.read()


setup(
    name="yarfox",
    version="1.0.1",
    description="Cross-post from Mastodon to twitter",
    long_description=get_long_description(),
    url="https://github.com/dmerejkowsky/yarfox",
    author="Dimitri Merejkowsky",
    author_email="d.merej@gmail.com",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "lxml",
        "mastodon.py",
        "oauth2",
        "path.py",
        "python-cli-ui",
        "pyxdg",
        "ruamel.yaml",
        "twitter",
    ],
    entry_points={"console_scripts": ["yarfox = yarfox.cli:main"]},
)
