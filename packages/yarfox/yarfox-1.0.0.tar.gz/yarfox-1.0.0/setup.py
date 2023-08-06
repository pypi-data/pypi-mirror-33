import sys
from setuptools import setup, find_packages

if sys.version_info.major < 2:
    sys.exit("Error: Please upgrade to Python3")


setup(
    name="yarfox",
    version="1.0.0",
    description="Cross-post from Mastodon to twitter",
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
