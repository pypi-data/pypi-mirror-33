try: # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError: # for pip <= 9.0.3
    from pip.req import parse_requirements

from setuptools import setup

from class_pool import version

with open("README.md", "r") as fh:
    long_description = fh.read()

dependencies = parse_requirements('requirements.txt', session=False)

setup(
    name='class-pool',
    version=version.__version__,
    packages=['class_pool'],
    url='',
    author='Pawel Pecio',
    author_email='',
    long_description=long_description,
    long_description_content_type="text/markdown",
    description='Simple implementation of class pools for Python. Optional support for Django and DRF (if available)',
    zip_safe=False,
    install_requires=[str(ir.req) for ir in dependencies],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ]
)
