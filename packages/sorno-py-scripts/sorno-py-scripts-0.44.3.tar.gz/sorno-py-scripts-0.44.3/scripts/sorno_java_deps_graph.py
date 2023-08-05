#!/usr/bin/env python
"""Prints the class dependency graph given a bunch of java source files.

This script depends on the library sorno-py-scripts. You can find out the
installation detail in https://github.com/hermantai/sorno-py-scripts.


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
import collections
import logging
import os
import re
import sys

from sorno import loggingutil


_log = logging.getLogger()
_plain_logger = None  # will be created in main()
_plain_error_logger = None  # will be created in main()


class Graph(object):
    def __init__(self):
        self.nodes = set()
        self.edges = collections.defaultdict(set)

    def add_node(self, n):
        self.nodes.add(n)

    def add_edge(self, src, dst):
        self.nodes.add(src)
        self.nodes.add(dst)

        self.edges[src].add(dst)

    def get_edges(self, n):
        return [(n, d) for d in self.edges[n]]


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
        m = self.create_classes_to_contents_map(self.args.path)
        g = self.extract_class_dependency_graph(m)
        indegrees = self.get_indegrees(g)
        if self.args.edges:
            for n in g.nodes:
                for _, dst in g.get_edges(n):
                    print(n, "->", dst)
        else:
            self.print_graph(g, indegrees)

        return 0

    def create_classes_to_contents_map(self, paths):
        m = {}
        for path in paths:
            if os.path.isdir(path):
                for root, dirs, files in os.walk(path):
                    for f in files:
                        self._set_class_to_content(m, os.path.join(root, f))
            else:
                self._set_class_to_content(m, path)

        return m

    def _set_class_to_content(self, classes_to_contents_map, filepath):
        name, ext = os.path.splitext(filepath)
        if ext != ".java":
            return

        classes_to_contents_map[os.path.basename(name)] = open(filepath).read()

    def extract_class_dependency_graph(self, classes_to_contents_map):
        g = Graph()
        for c in classes_to_contents_map:
            g.add_node(c)

        for c, content in classes_to_contents_map.iteritems():
            for n in g.nodes:
                if c == n:
                    continue
                if re.search(r"\b%s\b" % n, content):
                    g.add_edge(c, n)

        return g

    def get_indegrees(self, graph):
        indegrees = collections.defaultdict(lambda: 0)
        for n in graph.nodes:
            for _, dst in graph.get_edges(n):
                indegrees[dst] += 1

        return indegrees

    def print_graph(self, graph, indegrees):
        for n in graph.nodes:
            if indegrees[n]:
                continue

            print(n)
            self.print_edges(graph, n, 4)
            print("-" * 40)
        return

    def print_edges(self, graph, node, indent=0):
        for _, dst in graph.get_edges(node):
            print(" " * indent + "->", dst)
            self.print_edges(graph, dst, indent + 4)

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
        "--edges",
        action="store_true",
        help="Print the edges instead of the graph",
    )
    parser.add_argument(
        "path",
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
