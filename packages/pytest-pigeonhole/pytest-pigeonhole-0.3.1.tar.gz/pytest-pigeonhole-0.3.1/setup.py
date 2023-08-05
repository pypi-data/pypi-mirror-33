from setuptools import setup

long_description = """
Pigeonhole
==========

``pytest-pigeonhole`` is a pytest plugin that adds a terminal-summary in
whose outcomes are split along given fixture value.

It can be helpful if use parameterized fixtures with larger scope.

.. image:: https://gitlab.com/kamichal/pigeonhole/badges/master/pipeline.svg
    :target: https://gitlab.com/kamichal/pigeonhole/
    :alt: pipeline status
.. image:: https://img.shields.io/pypi/pyversions/pytest-pigeonhole.svg
    :target: https://pypi.org/project/pytest-pigeonhole/
    :alt: python versions
.. image:: https://img.shields.io/pypi/v/pytest-pigeonhole.svg
    :target: https://pypi.org/project/pytest-pigeonhole/
    :alt: package version
.. image:: https://img.shields.io/pypi/status/pytest-pigeonhole.svg
    :target: https://gitlab.com/kamichal/pigeonhole/
    :alt: development status

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
    version="0.3.1",
)
