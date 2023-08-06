from setuptools import setup

with open('README.rst', 'r') as infile:
    long_des = infile.read()

setup(
    name='pydogs',
    description='A Delaunay based approach of hyperparmeter optimization',
    long_description=long_des,
    version='0.1.4',
    url='https://github.com/deltadogs/pyDOGS4',
    author='Shahrouz Ryan Alimo',
    author_email='salimoha@ucsd.edu',
    packages=['pydogs']
)
