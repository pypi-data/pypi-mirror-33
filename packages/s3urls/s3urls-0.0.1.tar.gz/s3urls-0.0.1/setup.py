from setuptools import setup

NAME = 's3urls'
VERSION = '0.0.1'
AUTHOR = 'Ben Steadman'
EMAIL = 'steadmanben1@gmail.com'
URL = 'https://github.com/ButoVideo/s3urls'
REQUIRES_PYTHON = '>=3.6.0'

with open("README.md", "r") as f:
    long_description = f.read()

setup(
    name=NAME,
    version=VERSION,
    author=AUTHOR,
    author_email=EMAIL,
    long_description=long_description,
    long_description_content_type="text/markdown",
    url=URL,
    python_requires=REQUIRES_PYTHON,
    py_modules=['s3urls'],
    license='MIT',
    classifiers=(
        "Programming Language :: Python :: 3.6",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Topic :: Utilities",
    ),
)
