from setuptools import setup,setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='toto9',
    version='0.1.2',
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
        'google-api-python-client>=1.7.3',
        'google-auth>=1.5.0',
        'google-auth-httplib2>=0.0.3',
        'retrying>=1.3.3',
        'httplib2>=0.11.3'
    ]
)
