from setuptools import find_packages, setup


setup(
    name='pdfrw_test_data',
    version='0.0.1',
    packages=find_packages(),
    package_data={
        '': 'global/*.pdf',
    }
)
