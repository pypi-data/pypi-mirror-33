#!/usr/bin/env python
"""Join the malls information in different csv files.

The first line of each csv file should be the headers. One of the header should
be "Name".

Sample run:
    sorno_join_malls_info_in_csv.py --columns-kept-last "Total Mall Store GLA" *.csv

    Copyright 2016 Heung Ming Tai

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
import csv
import logging
import os
import re
import string
import sys

from sorno import algo
from sorno import consoleutil
from sorno import loggingutil


_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class App(object):
    """A console application to do work"""
    def __init__(self, args):
        """
        Args:
            args (argparse.Namespace): The flags for the script.
        """
        self.args = args

    def run(self):
        filepaths = sorted(
            self.args.files,
            reverse=True,
            key=lambda k: os.path.basename(k),
        )
        mall_names = []
        # A map of adjusted mall names to mall_info
        # An adjusted mall name is the value returned by
        # self.get_mall_name_for_matching(original_mall_name)
        # mall_info is a list of values of the mall
        mall_infos = {}

        is_last_file = True
        num_of_placeholders = 0
        num_of_placeholders_for_next_row = 0
        headers = ["Name"]
        if self.args.columns_kept_last:
            for col in sorted(self.args.columns_kept_last):
                headers.append(col)

        for filepath in filepaths:
            num_str = self.get_number_string_from_s(os.path.basename(filepath))
            _log.info("Process [%s]", num_str)
            with open(filepath) as f:
                reader = csv.DictReader(row_processor(f))
                is_first_row_encountered = False
                for row in reader:
                    mall_name = row['Name']
                    mall_info = self.get_mall_info(mall_name, mall_infos)
                    if not mall_info:
                        mall_names.append(mall_name)
                        mall_info.append(mall_name)

                    if num_of_placeholders and (
                        num_of_placeholders > len(mall_info)
                    ):
                        mall_info.extend(
                            [""] * (num_of_placeholders - len(mall_info))
                        )

                    if is_last_file:
                        if self.args.columns_kept_last:
                            for col in sorted(self.args.columns_kept_last):
                                mall_info.append(row[col])
                                del row[col]
                    else:
                        self.exclude_columns_kept_last(row)

                    # populate the rest of the fields
                    del row['Name']
                    for col in sorted(row.keys()):
                        mall_info.append(row[col])
                        if not is_first_row_encountered:
                            headers.append(num_str + " " + col)

                    if not is_first_row_encountered:
                        is_first_row_encountered = True
                    num_of_placeholders_for_next_row = len(mall_info)

            num_of_placeholders = num_of_placeholders_for_next_row

            if is_last_file:
                is_last_file = False

        print("\t".join(headers))
        for mall_name in mall_names:
            for_matching = self.get_mall_name_for_matching(mall_name)
            mall_info = mall_infos[for_matching]

            print(
                "\t".join(
                    [c.replace("\n", ", ").replace(" ,", "") for c in mall_info]
                )
            )

        return 0

    def get_mall_info(self, mall_name, mall_infos):
        name_for_matching = self.get_mall_name_for_matching(mall_name)

        mall_info = mall_infos.get(name_for_matching)
        if mall_info is not None:
            return mall_info

        # use min edit distance to see if we can find a mall info
        for name in mall_infos:
            d = algo.min_edit_distance_dp(name_for_matching, name)
            if d / len(name) < 0.3:
                if consoleutil.confirm(
                    "Does name [%s] match [%s]?" % (
                        re.sub(r"\s+", " ", mall_name),
                        # the first field of mall_info must be a name
                        re.sub(r"\s+", " ", mall_infos[name][0]),
                    ),
                    file=sys.stderr,
                ):
                    mall_info = mall_infos[name]
                    mall_infos[name_for_matching] = mall_info
                    return mall_info

        mall_info = []
        mall_infos[name_for_matching] = mall_info
        return mall_info

    def exclude_columns_kept_last(self, info):
        if self.args.columns_kept_last:
            for col in self.args.columns_kept_last:
                if col in info:
                    del info[col]

    def get_mall_name_for_matching(self, name):
        return "".join(name.split()).lower()

    def get_number_string_from_s(self, s):
        l = 0
        r = 0
        for i, c in enumerate(s):
            if c in string.digits:
                l = i
                break

        for i, c in reversed(list(enumerate(s))):
            if c in string.digits:
                r = i + 1
                break

        if l == r:
            return s

        return s[l:r]

def row_processor(unicode_csv_data):
    for line in unicode_csv_data:
        yield re.sub(
            r"\(\d+\)",
            "",
            line.decode('utf-8').replace("\u2019","'").encode('utf-8'),
        ).replace("*","")

def parse_args(cmd_args):
    description = __doc__.split("Copyright 2016")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument(
        "--columns-kept-last",
        help="The columns which are kept only for the last file",
        action="append",
    )
    parser.add_argument(
        "files",
        nargs="+",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _plain_logger, _plain_error_logger

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)
    _plain_logger = loggingutil.create_plain_logger(
        "PLAIN",
        debug=args.debug,
    )
    _plain_error_logger = loggingutil.create_plain_logger(
        "PLAIN_ERROR",
        debug=args.debug,
        stdout=False,
    )

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
