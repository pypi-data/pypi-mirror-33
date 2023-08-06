import setuptools

with open('README.md', 'r') as file:
    long_description = file.read()

setuptools.setup(
    name = 'argvparser',
    version = '0.2.2',
    author = 'Arthuchaut',
    description = 'This module allows to format an argument vector in a structure easier to read and use for command line applications',
    long_description = long_description,
    long_description_content_type = 'text/markdown',
    url = 'https://github.com/Arthuchaut/ArgvParser',
    packages = setuptools.find_packages(),
    license = 'MIT',
    classifiers = (
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    )
)