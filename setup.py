from setuptools import setup, find_packages


setup(
    name='stancli',
    version='0.0.1',
    packages=find_packages(),
    include_package_data=True,
    py_modules=[
        'stancli',
    ],
    install_requires=[
        'Click==7.0',
        'Pygments==2.4.2',
        'asyncio-nats-client==0.9.2',
        'asyncio-nats-streaming==0.4.0',
        'colorama==0.4.1',
        'ed25519==1.5',
        'idna==2.8',
        'multidict==4.5.2',
        'nkeys==0.1.0',
        'protobuf==3.8.0',
        'six==1.12.0',
        'yarl==1.3.0',
    ],
    entrypoints='''
    [console_scripts]
    stancli=stancli:cli
    ''',
)
