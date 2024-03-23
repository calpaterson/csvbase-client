import pathlib

from setuptools import setup, find_packages

VERSION = (
    (pathlib.Path(__file__).parent / "csvbase_client" / "VERSION").open().read().strip()
)

# The tests test the blog, so it must be installed
test_reqs = [
    "black",
    "bpython",
    "mypy",
    "pytest",
    "ruff",
    "types-requests",
    "types-setuptools",
    "types-toml",
    "pandas",
    "pyarrow",
    "types-passlib",
    "pandas-stubs",
]

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

# long agpl trove classifier that ruff doesn't like
c = "License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)"

setup(
    name="csvbase-client",
    version=VERSION,
    author="Cal Paterson",
    author_email="cal@calpaterson.com",
    description="The command line client for csvbase",
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    url="https://github.com/calpaterson/csvbase-client",
    keywords="csv data processing",
    package_data={"csvbase_client": ["VERSION"]},
    install_requires=[
        "click",
        "platformdirs",
        "pyappcache",
        "requests",
        "toml",
        "importlib_resources; python_version<'3.9'",
        "fsspec",
        "rich",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        c,
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Utilities",
    ],
    project_urls={
        "Bug Tracker": "https://github.com/calpaterson/csvbase-client/issues",
        "Documentation": "https://github.com/calpaterson/csvbase-client/wiki",
        "Source Code": "https://github.com/calpaterson/csvbase-client",
        "Changelog": "https://github.com/calpaterson/csvbase-client/blob/main/CHANGELOG.md",
    },
    extras_require={"tests": test_reqs},
    entry_points={
        "console_scripts": [
            "csvbase-client=csvbase_client.internals.cli:cli",
        ],
        "fsspec.specs": [
            "csvbase=csvbase_client.fsspec.CSVBaseFileSystem",
        ],
    },
)
