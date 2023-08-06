import setuptools


long_description = """
# test.helper.coverage

Class for autotests with incremental coverage call for python apps

"""

setuptools.setup(
    name = 'tester_coverage',
    version = '1.0',
    author = 'Vitaly Bogomolov',
    author_email = 'mail@vitaly-bogomolov.ru',
    description = 'Class for autotests with incremental coverage call for python apps',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/vb64/test.helper.coverage',
    packages = ['tester_coverage'],
    download_url = 'https://github.com/vb64/test.helper.coverage/archive/v1.0.tar.gz',
    keywords = ['python', 'Python27', 'coverage', 'unittest'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
