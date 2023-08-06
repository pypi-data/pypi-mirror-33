import setuptools


long_description = """
# test.helper.flask

Class for autotests flask python apps

"""

setuptools.setup(
    name = 'tester_flask',
    version = '1.0',
    author = 'Vitaly Bogomolov',
    author_email = 'mail@vitaly-bogomolov.ru',
    description = 'Class for autotests flask python apps',
    long_description=long_description,
    long_description_content_type="text/markdown",
    url = 'https://github.com/vb64/test.helper.flask',
    packages = ['tester_flask'],
    download_url = 'https://github.com/vb64/test.helper.flask/archive/v1.0.tar.gz',
    keywords = ['python', 'Python27', 'flask', 'unittest'],
    classifiers=[
        "Programming Language :: Python :: 2.7",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
)
