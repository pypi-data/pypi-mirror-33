# pylint: disable=C0111
from setuptools import setup

with open("README.md", "r") as fh:
    README = fh.read()

setup(
    name='oneforge',
    version='0.1.0',
    description='1Forge REST API wrapper',
    long_description=README,
    long_description_content_type='text/markdown',
    author='Renato Orgito',
    author_email='orgito@gmail.com',
    maintainer='Renato Orgito',
    maintainer_email='orgito@gmail.com',
    url='https://github.com/orgito/1forge-client',
    license='MIT',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.6',
        'Topic :: Software Development :: Libraries',
    ],
    keywords='1forge forex',
    packages=['oneforge'],
    setup_requires=['setuptools>=38.6.0'],
    install_requires=['requests'],
    python_requires='>=3.6',
    project_urls={
        'Bug Reports': 'https://github.com/orgito/1forge-client/issues',
        'Source': 'https://github.com/orgito/1forge-client',
    },
)
