from setuptools import setup, find_packages

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name="create_project",
    version="0.0.1",
    author="Justine T Kizhakkinedath",
    author_email="justinethomas009@gmail.com",
    description="Create a new project in gitlab with all your preferred \
    settings",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://gitlab.com/justinethomas/create_project",
    packages=find_packages(exclude=["contrib", "docs", "tests"]),
    classifiers=(
        "Development Status :: 3 - Alpha",
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
    keywords="project creation",
    entry_points={
        "console_scripts": [
            "create = create_project.__main__:main"
        ],
    },
    project_urls={
        "Bug Reports": "https://gitlab.com/justinethomas/create_project/issues",
        "Say Thanks!": "http://saythanks.io/to/justinethomas",
        "Source": "https://gitlab.com/justinethomas/create_project",
    },
)
