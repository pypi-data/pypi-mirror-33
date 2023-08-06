#!/usr/bin/env python
# -*- coding:utf8 -*-

#      Copyright 2018, Schuberg Philis BV
#
#      Licensed to the Apache Software Foundation (ASF) under one
#      or more contributor license agreements.  See the NOTICE file
#      distributed with this work for additional information
#      regarding copyright ownership.  The ASF licenses this file
#      to you under the Apache License, Version 2.0 (the
#      "License"); you may not use this file except in compliance
#      with the License.  You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
#      Unless required by applicable law or agreed to in writing,
#      software distributed under the License is distributed on an
#      "AS IS" BASIS, WITHOUT WARRANTIES OR CONDITIONS OF ANY
#      KIND, either express or implied.  See the License for the
#      specific language governing permissions and limitations
#      under the License.

#      Romero Galiza Jr. - rgaliza@schubergphilis.com

from setuptools import setup, find_packages

with open('README.md', 'r') as fd:
    long_description = fd.read()

base_url = 'https://github.com/romerojunior/ctrshif'
version_tag = '0.0.2'

setup(
    name='ctrshif',
    version=version_tag,
    description='Find and replace command line tool',
    long_description=long_description,
    long_description_content_type="text/markdown",
    author='Romero Galiza Jr',
    author_email='rgaliza@schubergphilis.com',
    license='Apache License Version 2.0',
    url=base_url,
    download_url=base_url + '/archive/' + version_tag + '.tar.gz',
    packages=find_packages(),
    install_requires=[
        'colorama',
    ],
    keywords=['templating', 'configparse'],
    platforms=['Any'],
    scripts=['bin/ctrshif'],
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Topic :: Text Processing"
    )
)