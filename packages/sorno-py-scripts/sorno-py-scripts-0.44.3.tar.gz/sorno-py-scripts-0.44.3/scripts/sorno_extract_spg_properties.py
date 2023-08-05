#!/usr/bin/env python
"""Extracts Simon Property Group property information from its 10-K filings

Sample usage::

    $ sorno_extract_spg_properties.py spg_10-k.html

If you get UnicodeEncodingError, you should prefix your command with
"PYTHONIOENCODING=UTF-8". E.g::

    $ PYTHONIOENCODING=UTF-8 sorno_extract_spg_properties.py html_file


    Copyright 2017 Heung Ming Tai

    Licensed under the Apache License, Version 2.0 (the "License");
    you may not use this file except in compliance with the License.
    You may obtain a copy of the License at

        http://www.apache.org/licenses/LICENSE-2.0

    Unless required by applicable law or agreed to in writing, software
    distributed under the License is distributed on an "AS IS" BASIS,
    WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
    See the License for the specific language governing permissions and
    limitations under the License.
"""
from __future__ import print_function
from __future__ import absolute_import
from __future__ import division
from __future__ import unicode_literals

import argparse

import re
import sys
import subprocess

from bs4 import BeautifulSoup

class App(object):
    def __init__(self, args):
        self.args = args

    def run(self):
        soup = BeautifulSoup(open(self.args.html_file).read(), "lxml")
        tables = soup.find_all("table")
        property_tables = [t for t in tables if "Property Name" in self.compress_spaces(t.text)]
        for property_table in property_tables:
            self.print_property_table(property_table)
        return 0

    def print_property_table(self, property_table):
        for tr in property_table.find_all("tr"):
            print("\t".join([self.compress_spaces(td.text).strip() for td in tr.find_all("td")]))

    def compress_spaces(self, s):
        return re.sub(r"\s+", " ", s.replace(u"\xa0", " "))


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2017")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument("html_file")

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
