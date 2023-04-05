import pathlib

from setuptools import setup, find_packages

VERSION = (pathlib.Path(__file__).parent / "csvbasec" / "VERSION").open().read().strip()

# The tests test the blog, so it must be installed
test_reqs = [
    "bandit==1.7.4",
    "black==22.3.0",
    "bpython~=0.22.1",
    "feedparser==6.0.2",
    "mypy==0.982",
    "openpyxl==3.1.2",
    "pandas==1.3.5",
    "pytest==7.1.1",
    "types-setuptools==65.1.0",
    "types-toml==0.10.8.5",
    "types-requests",
]

setup(
    name="csvbasec",
    version=VERSION,
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    install_requires=[
        "click",
        "platformdirs",
        "requests",
        "toml",
        "typing-extensions",
    ],
    extras_require={"tests": test_reqs},
    entry_points={
        "console_scripts": [
            "csvbasec=csvbasec.internals.cli:cli",
        ]
    },
)
