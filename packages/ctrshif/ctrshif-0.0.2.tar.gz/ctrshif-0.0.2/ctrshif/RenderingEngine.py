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

import re
import abc

from ctrshif.AttributeFile import AttributeFile
from ctrshif.TemplateFile import TemplateFile


class RenderingEngine(object):

    __metaclass__ = abc.ABCMeta

    def __init__(self, attribute, section, template):
        """ Defines the contract for rendering methods. Each rending method
        should only take an instance of `AttributeFile` and `TemplateFile`.

        :param attribute:     instance of AttributeFile
        :type host_list:      AttributeFile
        :param section:       section of the attribute file
        :type section:        str
        :param template:      instance of TemplateFile
        :type template:       TemplateFile
        """
        self.attribute = attribute
        self.section = section
        self.template = template

    @abc.abstractmethod
    def render(self):
         """Renders the file with a mapping of variables."""


class AttributeSubstitution(RenderingEngine):

    def __init__(self, attribute, section, template):
        super(AttributeSubstitution, self).__init__(
            attribute, section, template
        )

    def _repl(self, match):

        mapping = self.attribute.list_attributes(section=self.section)

        if match.group(1).strip() in mapping:
            result = mapping[match.group(1).strip()]
        else:
            result = match.group(0)

        return result

    def render(self, dry_run=False):

        content = re.sub(
            pattern=self.template.delimiter_pattern,
            repl=self._repl,
            string=self.template.read_content()
        )

        if dry_run:
            self.template.print_content(content)
        else:
            self.template.write_content(content)


if __name__ == "__main__":
    pass