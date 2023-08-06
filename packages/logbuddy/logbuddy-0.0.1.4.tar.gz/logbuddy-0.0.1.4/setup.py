from setuptools import setup

with open("README.md", "r") as fh:
    long_description = fh.read()

setup(
    name='logbuddy',
    version='0.0.1.4',
    description='Loghandler',
    license='MIT',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=['logbuddy'],
    author='buddyspencer',
    author_email='buddyspencer@protonmail.com',
    keywords=['example'],
    url='https://gitlab.com/buddyspencer/logbuddy.git'
)