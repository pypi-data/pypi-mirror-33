import setuptools


with open("README.md", "r") as fhandle:
    long_description = fhandle.read()

setuptools.setup(
    name = 'tester_gae',
    version = '1.0',
    author = 'Vitaly Bogomolov',
    author_email = 'mail@vitaly-bogomolov.ru',
    description = 'Class for autotests GoogleAppEngine platform python apps',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/vb64/test.helper.gae',
    packages = ['tester_gae'],
    download_url = 'https://github.com/vb64/test.helper.gae/archive/v1.0.tar.gz',
    keywords = ['python', 'Python27', 'GAE', 'GoogleAppEngine', 'unittest'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
