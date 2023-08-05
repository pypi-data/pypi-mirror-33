from setuptools import setup

setup(
    name='binary-to-string',
    version='0.1',
    packages=['binary_to_string'],
    url='',
    install_requires=['scikit-learn>=0.19.1', 'numpy>=1.14.3'],
    license='BSD 3',
    author='Mahmoud KOBBI',
    author_email='mahmoud.kobbi@ibm.com',
    description='This package transforms bytes into a string to integrate to a sklearn Pipeline'
)
