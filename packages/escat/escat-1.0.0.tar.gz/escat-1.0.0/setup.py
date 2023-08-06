import setuptools
import os

with open('README.md', 'r') as fh:
    long_description = fh.read()

setuptools.setup(
    name='escat',
    version='1.0.0',
    author='Anish Mashankar',
    scripts=["bin/escat"],
    description='Command line wrapper for Elasticsearch CAT API',
    long_description=long_description,
    url='https://github.com/itisanish/escat',
    packages=setuptools.find_packages(),
    python_requires='>=3.0',
    data_files=[(os.path.join(os.path.expanduser("~"), ".escat"), ["resources/config.yml"])],
    classifiers=(
        'Programming Language :: Python :: 3',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
    ),
    install_requires=[
        "elasticsearch",
        "pyyaml"
    ]
)
