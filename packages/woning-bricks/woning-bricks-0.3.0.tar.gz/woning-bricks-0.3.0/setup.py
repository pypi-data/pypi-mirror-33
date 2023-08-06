from setuptools import setup, find_packages

setup(
    name='woning-bricks',
    description='Development workflow made easy',
    long_description=open('README.rst').read(),
    long_description_content_type='text/x-rst',
    url='https://gitlab.com/woning-group/libs/bricks',
    version='0.3.0',
    packages=find_packages(),
    install_requires=[
        'click>=6',
        'woning-wattle>=0.4',
        'colorlog',
    ],
    extras_require={
        'dev': [
            'pytest',
            'pycodestyle',
            'woning-bricks',
            'twine',
            'bumpversion'
        ]
    },
    entry_points={
        'console_scripts': [
            'bricks = bricks.main:cli'
        ]
    }
)
