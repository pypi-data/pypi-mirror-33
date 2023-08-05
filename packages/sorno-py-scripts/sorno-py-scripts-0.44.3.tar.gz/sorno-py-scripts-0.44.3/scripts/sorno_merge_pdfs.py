#!/usr/bin/env python
"""Merge pdfs

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
import logging
from os import path
import subprocess
import sys

from sorno import loggingutil
import pyPdf


_log = logging.getLogger()


class App(object):
    """A console application to do work"""
    def __init__(self, args):
        """
        Args:
            args (argparse.Namespace): The flags for the script.
        """
        self.args = args

    def run(self):
        """The entry point of the script
        """
        out = pyPdf.PdfFileWriter()

        for pdf_file in self.args.pdf_file:
            _log.info("Read %s", pdf_file)
            # cannot close the file before writing
            f = open(pdf_file, "rb")
            pdf_f = pyPdf.PdfFileReader(f)
            if pdf_f.isEncrypted:
                try:
                    pdf_f.decrypt("")
                except NotImplementedError:
                    f.close()
                    new_pdf_file = pdf_file + ".decrypted"
                    _log.info("Decrypt with qpdf and output to: %s", new_pdf_file)
                    subprocess.check_call(['qpdf', "--password=", '--decrypt', pdf_file, new_pdf_file])
                    new_f = open(new_pdf_file, "rb")
                    pdf_f = pyPdf.PdfFileReader(new_f)
            for i in range(pdf_f.numPages):
                out.addPage(pdf_f.getPage(i))

        out.write(open(self.args.output_file, "wb"))
        return 0

def parse_args(cmd_args):
    description = __doc__.split("Copyright 2017")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )
    parser.add_argument("output_file")
    parser.add_argument("pdf_file", nargs="+")

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
