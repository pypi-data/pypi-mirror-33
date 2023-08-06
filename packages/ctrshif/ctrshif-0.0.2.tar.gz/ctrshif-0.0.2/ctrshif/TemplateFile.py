#!/usr/bin/env python3

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

import os
import re
import colorama
import codecs


class TemplateFile(object):

    colorama.init(autoreset=True)

    def __init__(self, path, encoding='iso-8859-1'):
        self.path = path
        self.prefix_delimiter = '<%='
        self.suffix_delimiter = '%>'
        self.no_delimiters = False
        self.encoding = encoding

    @property
    def delimiter_pattern(self):
        """ Only contains one parenthesized group `(.+?)` which holds the
            attribute that needs replacement.
        """
        if self.no_delimiters:
            pattern = r"([\w'-]+)"
        else:
            pattern = re.escape(self.prefix_delimiter) \
                + r"(.+?)" + re.escape(self.suffix_delimiter)
        return pattern

    def read_content(self):
        with codecs.open(
            self.path,
            mode='r',
            encoding=self.encoding,
            errors='strict'
        ) as fd:
            content = fd.read()
        return content

    def write_content(self, content):
        with open(self.path, 'w') as fd:
            fd.write(content)

    def print_content(self, content):
        print(colorama.Fore.GREEN + "# {path}".format(path=self.path))
        print("{content}".format(content=content))


if __name__ == "__main__":
    pass