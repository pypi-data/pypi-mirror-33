from setuptools import setup

long_description = open("README.rst").read()

setup(
    author="Michal Kaczmarczyk",
    author_email="michal.s.kaczmarczyk@gmail.com",
    classifiers=[
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python",
        "Topic :: Software Development :: Testing",
    ],
    entry_points={"pytest11": ["pigeonhole = pigeonhole.plugin"]},
    install_requires=[
        "pytest>=3.4",
    ],
    long_description=long_description,
    name="pytest-pigeonhole",
    packages=["pigeonhole"],
    url="https://gitlab.com/kamichal/pigeonhole",
    version="0.2",
)
