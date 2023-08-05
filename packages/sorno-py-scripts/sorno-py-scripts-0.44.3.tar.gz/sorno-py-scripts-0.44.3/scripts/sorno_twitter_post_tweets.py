#!/usr/bin/env python
"""Batch posting tweets on Twitter

Before using the script, go to
https://dev.twitter.com/oauth/overview/application-owner-access-tokens to get
the necessary credentials.

Use Google Doc to edit your tweets, one line per tweet. You should not use naked links (i.e. each link should be associated with some text). Then "File" -> "Download as" -> "Web Page (.html zipped)".

Unzip the downloaded file. Then run the following command with the appropriate parameters. path_to_file should be the path to the html file you unzipped.

	$ sorno_twitter_post_tweets.py --consumer-key consumer_key --consumer-secret consumer_secret --access_token-key access_token_key --access-token-secret access_token_secret --parse-tweets-from-file path_to_file

The script prints each tweet, and asks if you want to post the tweet indicated by "Tweet preview". Enter "y" if you want it posted, "n" otherwise.


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
from collections import namedtuple
import copy
import logging
import re
import subprocess
import sys
import urlparse

import twitter
import bs4

from sorno import consoleutil
from sorno import loggingutil


_log = logging.getLogger()

Tweet = namedtuple('Tweet', ['text', 'links', 'original_node'])


class App(object):
    """A console application to do work"""
    def __init__(self, args):
        """
        Args:
            args (argparse.Namespace): The flags for the script.
        """
        self.args = args
        self.api = None

    def run(self):
        """The entry point of the script"""
        args = self.args
        _log.debug("%s", args)
        self.api = twitter.Api(
            consumer_key=args.consumer_key,
            consumer_secret=args.consumer_secret,
            access_token_key=args.access_token_key,
            access_token_secret=args.access_token_secret,
        )
        user = self.api.VerifyCredentials()
        if user is None:
            _log.error("Invalid user credentials")
            return 1

        if args.parse_tweets_from_file:
            with open(args.parse_tweets_from_file) as f:
                content = f.read()

            soup = bs4.BeautifulSoup(content, 'html.parser')
            self.batch_tweeting_with_soup(soup)

        _log.debug("user %s", user)
        return 0

    def batch_tweeting_with_soup(self, soup):
        tweets = []
        for p in soup.find_all('p'):
            tweet = self.make_tweet(p, remove_anchored_text=self.args.remove_anchored_text)
            if not tweet.text:
                continue
            tweets.append(tweet)

        for i, tweet in enumerate(tweets):
            print("Tweet %s:" % (i + 1))
            self.post_tweet(tweet)
            print("\n" * 2)

    def make_tweet(self, node, remove_anchored_text=False):
        anchors = node.find_all('a')
        links = [self.clean_link(a['href']) for a in anchors]
        text = self.get_text(node, remove_anchored_text=remove_anchored_text)
        return Tweet(text=text, links=links, original_node=node)

    def get_text(self, node, remove_anchored_text=False):
        if remove_anchored_text:
            node = copy.copy(node)
            for anchor in node('a'):
                anchor.replaceWith("")

        return re.sub(r"\s+", " ", node.text.replace('\xa0', ' ')).strip()

    def clean_link(self, link):
        """
        Clean a link from something like:
        https://www.google.com/url?q=https://blahblah.com&sa=D&ust=1498545552302000&usg=AFQjCNE8sJX0-SzPOwH545Ek44d3gNXtMg to https://blahblah.com
        """
        url = urlparse.urlparse(link)
        params = {}
        if url.query:
            params = urlparse.parse_qs(url.query)

        if url.netloc == "www.google.com" and url.path == "/url" and params.get('q'):
            return params.get('q')[0]

        return link

    def post_tweet(self, tweet):
        print("Text:", tweet.text)
        print("Links:", tweet.links)
        status = tweet.text
        status_len = len(status)
        for link in tweet.links:
            status = self.join_text(status, link)
        status_with_links_len = len(status)

        print("Tweet preview(%s,%s): %s" % (status_len, status_with_links_len, status))

        ans = consoleutil.input("\nTweet it[yes/no/remove-anchored-text]? ")
        ans = ans.lower()
        if ans in ("y", "yes"):
            result = self.api.PostUpdate(status)
            print("Tweeted:", result.text)
            print("Result:", result)
        elif ans in ("n", "no"):
            return
        elif ans in ("r", "remove", "remove-anchored-text"):
            print("\n*Edited*\n")
            tweet = self.make_tweet(tweet.original_node, remove_anchored_text=True)
            self.post_tweet(tweet)

    def join_text(self, text, more_text):
        if text == "":
            return more_text
        return text + " " + more_text

    def _run_cmd(self, cmd):
        """Run a shell command

        Args:
            cmd (string or a list of strings): The shell command to run. If
                it's a string, uses the system shell to run the command. If
                it's a list of strings, the first string is the program to run
                and the rest are its arguments. The arguments are quoted
                properly by the subprocess module, so the arguments do not
                have to be quoted when passing to this method.
        """
        _log.info(cmd)
        if isinstance(cmd, list):
            use_shell = False
        else:
            use_shell = True
        return subprocess.check_call(cmd, shell=use_shell)


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
    parser.add_argument(
        "--consumer-key",
    )
    parser.add_argument(
        "--consumer-secret",
    )
    parser.add_argument(
        "--access-token-key",
    )
    parser.add_argument(
        "--access-token-secret",
    )
    parser.add_argument(
        "--parse-tweets-from-file",
    )
    parser.add_argument(
        "--remove-anchored-text",
        action="store_true",
    )

    args = parser.parse_args(cmd_args)
    return args


def main():
    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_log, debug=args.debug)

    app = App(args)
    sys.exit(app.run())


if __name__ == '__main__':
    main()
