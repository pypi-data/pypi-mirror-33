from setuptools import setup

setup(
    name='aws-top',
    version='0.2',
    packages=['aws_top'],
    install_requires=['boto3==1.7.20', 'urwid==2.0.1'],
    url='https://github.com/brennerm/aws-top',
    license='MIT',
    author='brennerm',
    author_email='xamrennerb@gmail.com',
    description='CLI Dashboard for AWS services'
)
