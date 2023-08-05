from setuptools import setup
import os
import sys

DESC = """SPF (Sender Policy Framework) processing engine for Postfix policy server implemented in Python."""

setup(name='spf-engine',
    version='2.1.0',
    description='SPF processing for Postfix',
    long_description=DESC,
    author='Scott Kitterman',
    author_email='scott@kitterman.com',
    url='https://launchpad.net/pypolicyd-spf',
    packages=['spf_engine'],
    keywords = ['Postfix','spf','email'],
    entry_points = {
        'console_scripts' : [
            'policyd-spf = spf_engine.policyd_spf:main',
        ]},
    data_files=[(os.path.join('share', 'man', 'man1'),
        ['policyd-spf.1']), (os.path.join('share', 'man', 'man5'),
        ['policyd-spf.conf.5']), (os.path.join('etc', 'python-policyd-spf'),
        ['policyd-spf.conf']), (os.path.join('share', 'man', 'man5'),
        ['policyd-spf.peruser.5'])],
    install_requires = 'pyspf',
    classifiers = [
        'Development Status :: 5 - Production/Stable',
        'Environment :: No Input/Output (Daemon)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache Software License',
        'Natural Language :: English',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3',
        'Topic :: Communications :: Email :: Mail Transport Agents',
        'Topic :: Communications :: Email :: Filters',
    ]
)

if sys.version_info < (3, 3):
    raise Exception("SPF engine requires python3.3 and later.")
