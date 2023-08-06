#!/usr/bin/env python

from setuptools import setup, find_packages

import metadata

setup(
    url=metadata.project_url,
    name=metadata.name,
    version=metadata.version,
    license=metadata.license,
    platforms=['OS Independent'],
    description=metadata.description,
    author=metadata.author,
    author_email=metadata.author_email,
    packages=find_packages(),
    install_requires=[
        'setuptools',
        'django-cms>=2.5',
        'django-classy-tags>=0.3.2',
        'django-haystack>=2.8',
    ],
    # Accept all data files and directories matched by MANIFEST.in or found in source control.
    include_package_data=True,
    package_dir={
        metadata.package_name:metadata.package_name,
    },
    zip_safe=False,
    classifiers=[
        'Framework :: Django',
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Affero General Public License v3 or later (AGPLv3+)',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Topic :: Internet :: WWW/HTTP',
    ]
)
