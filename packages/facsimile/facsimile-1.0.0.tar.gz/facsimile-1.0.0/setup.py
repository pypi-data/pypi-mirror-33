
from setuptools import setup, find_packages

version = open('config/VERSION').read().strip()
requirements = open('config/requirements.txt').read().split("\n")
test_requirements = open('config/requirements-test.txt').read().split("\n")

setup(
    name='facsimile',
    version=version,
    author='20C',
    author_email='code@20c.com',
    description='',
    long_description=open('README.txt').read(),
    license='LICENSE.txt',
    classifiers=[
        'Development Status :: 4 - Beta',
        'License :: OSI Approved :: Apache Software License',
    ],
    url='https://github.com/20c/facsimile',
    install_requires=requirements,
    test_requires=test_requirements,
    packages=find_packages(),
    package_data={'facsimile': ['script/*.sh']},
    scripts=['facsimile/bin/facs', 'facsimile/bin/version_bump_dev', 'facsimile/bin/version_merge_release'],
    zip_safe=False
)
