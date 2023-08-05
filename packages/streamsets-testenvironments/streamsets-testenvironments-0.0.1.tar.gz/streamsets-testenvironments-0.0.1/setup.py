# Copyright 2017 StreamSets Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""The setup script."""

from setuptools import setup

with open('README.rst') as readme_file:
    readme = readme_file.read()

with open('HISTORY.rst') as history_file:
    history = history_file.read()

requirements = [
    'colorlog',
    'clusterdock',
    'PyYAML',
    'python-dateutil',
    'requests'
]

setup_requirements = [
    'pytest-runner',
    # TODO: put setup requirements (distutils extensions, etc.) here
]

test_requirements = [
    'pytest',
    # TODO: put package test requirements here
]

setup(
    name='streamsets-testenvironments',
    version='0.0.1',
    description="Spin environments for StreamSets products",
    long_description=readme + '\n\n' + history,
    author='StreamSets, Inc.',
    author_email='eng-productivity@streamsets.com',
    url='https://github.com/streamsets/testenvironments',
    packages=['streamsets.testenvironments', 'streamsets.testenvironments.actions'],
    entry_points={'console_scripts': ['ste = streamsets.testenvironments.cli:main']},
    include_package_data=True,
    install_requires=requirements,
    license='OSI Approved :: Apache Software License',
    zip_safe=False,
    keywords='ste',
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: Other/Proprietary License',
        'Natural Language :: English',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    test_suite='tests',
    tests_require=test_requirements,
    setup_requires=setup_requirements,
)
