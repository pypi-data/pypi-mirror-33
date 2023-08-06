from setuptools import setup


setup(
    name='dumb-pypi',
    version='1.3.1',
    author='Chris Kuehl',
    author_email='ckuehl@ocf.berkeley.edu',
    url='https://github.com/chriskuehl/dumb-pypi',
    packages=['dumb_pypi'],
    install_requires=[
        'distlib',
        'jinja2',
        'packaging',
    ],
    classifiers=[
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.6',
    ],
    entry_points={'console_scripts': ['dumb-pypi = dumb_pypi.main:main']},
    package_data={'dumb_pypi': ['templates/*']},
)
