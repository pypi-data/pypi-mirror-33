from setuptools import setup, find_packages

setup(
    name='padar_features',
    version='0.1.2',
    packages=find_packages(),
    include_package_data=True,
    description='Extension of feature computation to be used in padar package',
    long_description=open('README.md').read(),
    install_requires=[
        "pandas",
        "numpy",
        "scipy",
        "dask[complete]"
    ],
)