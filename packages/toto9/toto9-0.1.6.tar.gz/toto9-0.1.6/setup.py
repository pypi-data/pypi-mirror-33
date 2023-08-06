from setuptools import setup,setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='toto9',
    version='0.1.6',
    description='The missing GCP Python Client Library',
    url='https://gitlab.nordstrom.com/public-cloud/toto9',
    author='Nordstrom Cloud Engineering',
    author_email='cloudengineers@nordstrom.com',
    long_description=long_description,
    long_description_content_type="text/markdown",
    license='MIT',
    packages=setuptools.find_packages(),
    zip_safe=False,
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Natural Language :: English"
    ),
    install_requires=[
        'google-api-python-client',
        'google-auth',
        'google-auth-httplib2',
        'retrying',
        'httplib2'
    ]
)
