import pathlib

from setuptools import setup, find_packages

VERSION = (pathlib.Path(__file__).parent / "cbc" / "VERSION").open().read().strip()

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
]

setup(
    name="cbc",
    version=VERSION,
    packages=find_packages(exclude=["tests.*", "tests"]),
    include_package_data=True,
    install_requires=[
        "click",
        "platformdirs",
        "pyappcache",
        "requests",
        "toml",
    ],
    extras_require={"tests": test_reqs},
    entry_points={
        "console_scripts": [
            "cbc=cbc.internals.cli:cli",
        ]
    },
)
