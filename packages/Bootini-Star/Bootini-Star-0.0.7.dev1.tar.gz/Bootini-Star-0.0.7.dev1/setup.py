"""Setup module for Bootini Star."""
__author__ = 'Ralph Seichter'

import os

from setuptools import __version__, find_packages, setup

exec(open(os.path.join('bootini_star', 'version.py')).read())

setup(
    name='Bootini-Star',
    version=__version__,
    description="Inspect EVE Online mail and skill queues in a web browser.",
    long_description=("Inspect EVE Online mail and skill queues in a web"
                      " browser. Inspired by CCP's discontinued EVE Gate"
                      " web application."),
    author='Ralph Seichter',
    author_email='bootini-star@seichter.de',
    url='https://github.com/rseichter/bootini-star.git',
    license='MIT',
    python_requires='>=3.6',
    packages=find_packages(exclude=['tests', 'tmp', 'venv']),
    data_files=[
        ('Bootini-Star', ['LICENSE', 'wsgi.py',
                          'db-static/db-helper.sh',
                          'db-static/groups.json.bz2',
                          'db-static/types.json.bz2']),
    ],
    install_requires=[
        'Flask >= 1.0.2',
        'Flask-Bootstrap4 >= 4.0.2',
        'Flask-Login >= 0.4.1',
        'Flask-WTF >= 0.14.2',
        'passlib >= 1.7.1',
        'pymongo >= 3.6.1',
        'requests-oauthlib >= 0.8.0',
        'Werkzeug >= 0.14.1',
    ],
    include_package_data=True,
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Development Status :: 3 - Alpha',
        'Programming Language :: Python :: 3.4',
        'Intended Audience :: Developers',
    ],
    project_urls={
        'Source': 'https://github.com/rseichter/bootini-star.git'
    },
)
