from setuptools import setup

with open('README.md', 'r') as f:
    long_description = f.read()

setup(
    name='lo4container',
    version='0.1.6',
    url='https://gitlab.com/lo4p/lo4container',
    description='The simplest IoC in python',
    long_description=long_description,
    long_description_content_type='text/markdown',
    author='Phuong Huynh',
    author_email='lo4kings@gmail.com',
    license='MIT',
    packages=['lo4container'],
    zip_safe=False,
)
