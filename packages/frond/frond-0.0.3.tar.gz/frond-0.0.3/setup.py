import os
from setuptools import setup, find_packages

here = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(here, 'README.md')) as f:
    README = f.read()


setup(
    name='frond',
    version='0.0.3',
    description='Asynchronous Fan Out/In for Pyramid.',
    long_description=README,
    long_description_content_type="text/markdown",
    classifiers=[
        "Programming Language :: Python",
        "Programming Language :: Python :: 3 :: Only",
        "Framework :: Pyramid",
        "Topic :: Internet :: WWW/HTTP",
        "License :: OSI Approved :: MIT License",
    ],
    keywords="",
    author='Landreville',
    author_email='landreville@heyneat.ca',
    url='https://gitlab.com/landreville/frond',
    packages=find_packages(),
    include_package_data=True,
    zip_safe=False,
    install_requires=[]
)
