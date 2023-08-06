#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
setuptools script file
"""

from setuptools import setup, find_packages

setup(
    name='aliyunoss2-autoupload',
    namespace_packages=[],
    packages=find_packages('src'),
    package_dir={'': 'src'},

    description='Monitor files by wildcard patterns, upload them to ALIYUN OSS, then move to backup directory.',
    url='https://github.com/tanbro/aliyunoss2-autoupload',
    author='liu xue yan',
    author_email='liu_xue_yan@foxmail.com',
    license='AGPLv3+',
    keywords='aliyun oss autoupload',

    use_scm_version={
        # guess-next-dev:	automatically guesses the next development version (default)
        # post-release:	generates post release versions (adds postN)
        'version_scheme': 'guess-next-dev',
    },
    setup_requires=['pytest-runner', 'setuptools_scm', 'setuptools_scm_git_archive'],

    install_requires=[
        'oss2>=2.2.0',
        'PyYAML>=3.12',
        'marshmallow>=3.0.0b1',
        'futures;python_version<="2.7"',
    ],

    tests_require=[
        'pytest',
        'python-dotenv',
        'pathlib2;python_version<"3.4"',
    ],
    test_suite='tests',

    python_requires='>=2.7,!=3.0.*,!=3.1.*,!=3.2.*,!=3.3.*',

    entry_points={
        'console_scripts': [
            'aliyunoss2-autoupload = aliyunoss2_autoupload.__main__:main',
        ],
    },

    extras_require={},

    package_data={
        '': ['data/*/*']
    },

    classifiers=[
        # How mature is this project? Common values are
        #   3 - Alpha
        #   4 - Beta
        #   5 - Production/Stable
        'Development Status :: 5 - Production/Stable',

        # Indicate who your project is intended for
        'Intended Audience :: Developers',
        'Intended Audience :: System Administrators',
        'Topic :: Internet',
        'Topic :: Communications :: File Sharing',

        # Pick your license as you wish (should match "license" above)
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',

        # Specify the Python versions you support here. In particular, ensure
        # that you indicate whether you support Python 2, Python 3 or both.
        'Programming Language :: Python',
        'Programming Language :: Python :: 2',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
    ],
)
