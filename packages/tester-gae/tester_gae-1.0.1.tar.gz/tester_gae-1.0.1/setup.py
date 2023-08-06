import setuptools


long_description = """
# test.helper.gae

Class for autotests GoogleAppEngine platform python apps

GAE Cloud SDK must be installed: https://cloud.google.com/sdk/

`gcloud components install app-engine-python`

"""

setuptools.setup(
    name = 'tester_gae',
    version = '1.0.1',
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
