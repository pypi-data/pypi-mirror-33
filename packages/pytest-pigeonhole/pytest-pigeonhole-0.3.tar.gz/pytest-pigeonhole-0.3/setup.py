from setuptools import setup

long_description = """
Pigeonhole
==========

``pytest-pigeonhole`` is a pytest plugin that adds a terminal-summary in
whose outcomes are splitted along given fixture value.

It can be helpful if use parametrized fixtures with larger scope.

[|pipeline status|] (https://gitlab.com/kamichal/pigeonhole/)
[|python versions|] (https://pypi.org/project/pytest-pigeonhole/)
[|package version|] (https://pypi.org/project/pytest-pigeonhole/)
[|development status|] (https://gitlab.com/kamichal/pigeonhole/)
"""

setup(
    author="Michal Kaczmarczyk",
    author_email="michal.s.kaczmarczyk@gmail.com",
    classifiers=[
        "Development Status :: 5 - Production/Stable",
        "Framework :: Pytest",
        "Intended Audience :: Developers",
        "Programming Language :: Python :: 2.7",
        "Programming Language :: Python :: 3.5",
        "Programming Language :: Python :: 3.6",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: Implementation :: PyPy",
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
    version="0.3",
)
