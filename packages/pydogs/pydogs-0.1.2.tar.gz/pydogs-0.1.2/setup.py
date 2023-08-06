from setuptools import setup

with open('README.md', 'r') as infile:
    long_des = infile.read()

setup(
    name='pydogs',
    description='A Delaunay based approach of hyperparmeter optimization',
    long_description=long_des,
    version='0.1.2',
    url='https://github.com/deltadogs/pyDOGS4',
    maintainer='Andrew Hess',
    maintainer_email='ahess3815@gmail.com',
    author='Shahrouz Ryan Alimo',
    packages=['pydogs']
)
