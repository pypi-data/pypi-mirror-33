from setuptools import setup, find_packages


def get_long_description():
    with open("README.md", "r") as f:
        return f.read()


setup(
    name="flask_uauth",
    version="0.1.1",
    author="Panagiotis Matigakis",
    author_email="pmatigakis@gmail.com",
    description="Simple authentication to Flask REST apis",
    long_description=get_long_description(),
    long_description_content_type="text/markdown",
    url="https://github.com/pmatigakis/flask-uauth",
    packages=find_packages(exclude=["tests"]),
    install_requires=[
        "Flask>=0.11.1"
    ],
    tests_require=["nose"],
    test_suite="nose.collector",
    zip_safe=True,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    )
)
