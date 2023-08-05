from setuptools import setup, find_packages

setup(
    name='looptools',
    version='0.1.1',
    packages=find_packages(),
    install_requires=[
        'certifi==2018.4.16',
        'chardet==3.0.4',
        'idna==2.7',
        'pkginfo==1.4.2',
        'requests==2.19.1',
        'requests-toolbelt==0.8.0',
        'tqdm==4.23.4',
        'twine==1.11.0',
        'urllib3==1.23',
    ],
    url='https://github.com/mrstephenneal/looptools',
    license='MIT Licence',
    author='Stephen Neal',
    author_email='stephen@stephenneal.net',
    description='Helper utility functions for logging output, timing processes and counting iterations.'
)
