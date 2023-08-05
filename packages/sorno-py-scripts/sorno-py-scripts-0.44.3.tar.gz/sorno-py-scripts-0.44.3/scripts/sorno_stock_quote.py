#!/usr/bin/env python
"""Gets stock quotes and other information for stock symbols.

The script can print real-time or close to real-time stock quotes, historical
quotes, and also fundamental ratios for the stock (company).

TODO:
Use google api instead, e.g. http://www.google.com/finance/info?q=nasdaq:appl


    Copyright 2014 Heung Ming Tai

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

from cStringIO import StringIO

import csv
import datetime
import logging
import math
import sys
import subprocess

from bs4 import BeautifulSoup
import requests
from sorno import loggingutil
from sorno import consoleutil

_LOG = logging.getLogger(__name__)
_PLAIN_LOGGER = None  # will be created in main()
_PLAIN_ERROR_LOGGER = None  # will be created in main()


class StockApp(object):
    # https://code.google.com/p/yahoo-finance-managed/wiki/enumQuoteProperty
    FIELD_HEADERS = [
        ("name", "s"),
        ("price", "l1"),
        ("date", "d1"),
        ("time", "t1"),
        ("change", "c1"),
        ("changeInPercent", "c"),
        ("lastTradeRealtime", "k1"),
        ("changeRealtime", "c6"),
        ("changePercentRealtime", "k2"),
        ("open", "o"),
        ("high", "h"),
        ("low", "g"),
        ("volume", "v"),
        ("AverageDailyVolume", "a2"),
        # ("SharesOutstanding", "j2"), shares outstanding returns non-standard
        # csv value
        ("bidRealtime", "b3"),
        ("askRealtime", "b2"),
        ("YearLow", "j"),
        ("YearHigh", "k"),
        ("DilutedEPS", "e"),
        ("EPSEstimateCurrentYear", "e7"),
        ("EPSEstimateNextYear", "e8"),
        ("PERatio", "r"),
        ("PERatioRealtime", "r2"),
        ("ShortRatio", "s7"),
        ("DividendPayDate", "r1"),
        ("ExDividendDate", "q"),
    ]

    YAHOO_STOCK_QUOTE_CSV_API = "http://download.finance.yahoo.com/d/quotes.csv"
    YAHOO_STOCK_HISTORICAL_QUOTES_API = "http://ichart.yahoo.com/table.csv"
    YAHOO_STOCK_INSIDER_PURCHASES_PAGE_TEMPLATE = (
        "http://finance.yahoo.com/q/it?s=%s+Insider+Transactions"
    )

    QUANDL_STOCK_FUNDAMENTAL_API = "http://www.quandl.com/api/v1/datasets/OFDP/DMDRN_%s_ALLFINANCIALRATIOS.csv"

    def __init__(
        self,
        stock_symbol,
        print_fundamentals=False,
        print_history=False,
        print_kd=False,
        print_rsi=False,
        print_price_quote=True,
        num_of_days_for_history=30,
        print_insider_purchases=False,
    ):
        self.stock_symbol = stock_symbol

        self.print_fundamentals = print_fundamentals
        self.print_history = print_history
        self.print_kd = print_kd
        self.print_rsi = print_rsi
        self.print_price_quote = print_price_quote

        self.num_of_days_for_history = num_of_days_for_history
        self.print_insider_purchases = print_insider_purchases
        self.day_low = None
        self.day_high = None
        self.current_quote = None

    def run(self):
        if self.print_price_quote:
            resp = requests.get(
                self.YAHOO_STOCK_QUOTE_CSV_API,
                params={
                    's': self.stock_symbol,
                    'f': "".join([h[1] for h in self.FIELD_HEADERS]),
                    'e': ".csv",
                },
            )
            _LOG.debug("URL: %s", resp.url)

            text = resp.text.strip()
            headers = [h[0] for h in self.FIELD_HEADERS]

            lines = [",".join(headers), text]
            reader = csv.DictReader(lines)
            # there is only one row in the result
            d = list(reader)[0]

            for header in headers:
                _PLAIN_LOGGER.info("%s:\t%s", header, d[header])

            self.current_quote = float(d['price'])

            if d['high'] == "N/A":
                # we are right after the trading day
                return

            self.day_high = float(d['high'])
            self.day_low = float(d['low'])

        if self.print_fundamentals:
            resp = requests.get(
                self.QUANDL_STOCK_FUNDAMENTAL_API % self.stock_symbol.upper()
            )

            text = resp.text

            reader = csv.DictReader(text.split("\n"))

            rows = list(reader)
            rows.sort(key=lambda r: r['Date'])

            consoleutil.DataPrinter(rows).print_result(
                consoleutil.DataPrinter.PRINT_STYLE_VERBOSE
            )

        if not self.print_history and self.print_kd:
            _LOG.error(
                "In order to print stochastic oscillators, historical data"
                    " data has to be enabled (--history)"
            )
            return

        if not self.print_history and self.print_rsi:
            _LOG.error(
                "In order to print RSI, historical data"
                    " data has to be enabled (--history)"
            )
            return

        if self.print_history:
            _PLAIN_LOGGER.info("")
            self.print_historical_stock_quotes()

        if self.print_insider_purchases:
            _PLAIN_LOGGER.info("")
            self.print_insider_purchase_entries()

    def print_historical_stock_quotes(self):
        today = datetime.datetime.today()
        num_of_days_for_history = self.num_of_days_for_history
        if self.print_rsi:
            # make sure we have at least 250 data points before today
            num_of_days_for_history = max(310, self.num_of_days_for_history)
        starting_date = today - datetime.timedelta(num_of_days_for_history)

        params = {
            's': self.stock_symbol,
            'a': starting_date.month - 1,
            'b': starting_date.day,
            'c': starting_date.year,
            'd': today.month-1,
            'e': today.day,
            'f': today.year,
            'g': "d",  # daily quotes
            'ignore': ".csv",
        }

        resp = requests.get(
            self.YAHOO_STOCK_HISTORICAL_QUOTES_API,
            params=params,
        )

        _LOG.info("URL: %s", resp.url)

        # The csv data came in reverse chronlogical order and with the
        # following fields:
        # Date Open High Low Close Volume Adj-Close
        data = []
        headers = None
        for line in resp.text.split("\n"):
            if line:
                if not headers:
                    headers = line.split(',')
                    continue

                values = line.split(',')
                for i in (1, 2, 3, 4, 6):
                    values[i] = float(values[i])
                # volume should be an integer
                values[5] = int(values[5])
                data.append(values)

        if not data:
            return

        if self.print_kd or self.print_rsi:
            # The csv data came in reverse chronological order, so make reverse
            # it to calculate %k and %d chronologically.
            data.reverse()

            current_row = [
                "Current",
                float("nan"),
                self.day_high,
                self.day_low,
                self.current_quote,
                float("nan"),
                float("nan"),
            ]

            if self.print_kd:
                # The csv has the following fields:
                # Date Open High Low Close Volume Adj-Close
                lowest = None
                highest = None
                all_ks = []
                for i, row in enumerate(data):
                    if i < 13:
                        row.extend([float("nan")] * 2)
                        continue

                    data_in_period = data[i - 13:i + 1]
                    lowest = min([r[3] for r in data_in_period])
                    highest = max([r[2] for r in data_in_period])
                    current_close = row[4]
                    k = self.calculate_k(current_close, lowest, highest)
                    row.append(k)
                    all_ks.append(k)
                    if len(all_ks) >= 3:
                        # calculate %d
                        row.append(int(round(sum(all_ks[-3:]) / 3.0)))
                    else:
                        row.append(float("nan"))

                # Calculate current %k and %d
                if all_ks and self.day_high:
                    lowest = min(lowest, self.day_low)
                    highest = max(highest, self.day_high)
                    k = self.calculate_k(self.current_quote, lowest, highest)
                    current_row.append(k)
                    all_ks.append(k)
                    if len(all_ks) >= 3:
                        # calculate %d
                        current_row.append(int(round(sum(all_ks[-3:]) / 3.0)))
                    else:
                        current_row(float("nan"))

                headers.extend(["%k", "%d"])

            if self.print_rsi:
                # The csv has the following fields:
                # Date Open High Low Close Volume Adj-Close
                gain = 0.0
                loss = 0.0
                avg_gain = 0
                avg_loss = 0
                for i, row in enumerate(data):
                    if i == 0:
                        row.append(float("nan"))
                        if _LOG.isEnabledFor(logging.DEBUG):
                            row.extend([avg_gain, avg_loss])

                        continue

                    diff = data[i][4] - data[i-1][4]

                    if i <= 14:
                        if diff >= 0:
                            gain += diff
                        else:
                            loss += -1 * diff

                    if i < 14:
                        row.append(float("nan"))
                        if _LOG.isEnabledFor(logging.DEBUG):
                            row.extend([gain / float(i), loss / float(i)])
                        continue

                    if i == 14:
                        # first RS
                        avg_gain = gain / 14.0
                        avg_loss = loss / 14.0
                        row.append(self.calculate_rsi(avg_gain, avg_loss))
                        if _LOG.isEnabledFor(logging.DEBUG):
                            row.append(avg_gain)
                            row.append(avg_loss)
                        continue

                    # subsequent RS
                    if diff >= 0:
                        avg_gain = (avg_gain * 13 + diff) / 14.0
                        avg_loss = avg_loss * 13 / 14.0
                    else:
                        avg_gain = avg_gain * 13 / 14.0
                        avg_loss = (avg_loss * 13 + -1 * diff) / 14.0

                    row.append(self.calculate_rsi(avg_gain, avg_loss))
                    if _LOG.isEnabledFor(logging.DEBUG):
                        row.append(avg_gain)
                        row.append(avg_loss)

                if self.day_high:
                    current_diff = self.current_quote - data[-1][4]
                    if current_diff >= 0:
                        avg_gain = (avg_gain * 13 + current_diff) / 14.0
                        avg_loss = avg_loss * 13 / 14.0
                    else:
                        avg_gain = avg_gain * 13 / 14.0
                        avg_loss = (avg_loss * 13 + -1 * current_diff) / 14.0
                    current_row.append(self.calculate_rsi(avg_gain, avg_loss))
                    if _LOG.isEnabledFor(logging.DEBUG):
                        current_row.append(avg_gain)
                        current_row.append(avg_loss)

                headers.append("RSI")
                if _LOG.isEnabledFor(logging.DEBUG):
                    headers.append("avg_gain")
                    headers.append("avg_loss")

                if num_of_days_for_history > self.num_of_days_for_history:
                    # delete unnecessary rows
                    real_starting_date = today - datetime.timedelta(
                        self.num_of_days_for_history
                    )
                    d = real_starting_date.strftime("%Y-%m-%d")
                    for i, row in enumerate(data):
                        if row[0] >= d:
                            break

                    if i:
                        del data[0:i]

            # change it back to reverse chronlogical order
            data.append(current_row)
            data.reverse()

        # Format the data before printing them out
        out = [self.format_data_row(row) for row in data]
        consoleutil.DataPrinter(
            out,
            headers=headers,
            print_func=_PLAIN_LOGGER.info
        ).print_result()

    @staticmethod
    def format_data_row(row):
        new_row = []
        # The fields are:
        # Date Open High Low Close Volume Adj-Close
        # If self.print_kd is true, add two more fields: %k and %d
        for i in range(len(row)):
            if i == 0:
                # Date
                new_row.append(row[0])
                continue

            n = row[i]
            if math.isnan(n):
                new_row.append("N/A")
                continue

            if i in (5, 7, 8):
                new_row.append(str(n))
                continue

            new_row.append("{0:.2f}".format(n))

        return new_row

    def historical_data_row_for_printing(self, row):
        return "\t".join(
            [
                "{0:.2f}".format(float(c)) if "." in c else c
                for c in row
            ]
        )

    @staticmethod
    def calculate_k(current, lowest, highest):
        return int(
            round(
                (current - lowest) / (highest - lowest) * 100
            )
        )

    @staticmethod
    def calculate_rsi(avg_gain, avg_loss):
        if avg_loss == 0:
            return 100

        rs = avg_gain / float(avg_loss)
        return 100 - 100.0 / (1.0 + rs)

    def print_insider_purchase_entries(self):
        resp = requests.get(
            self.YAHOO_STOCK_INSIDER_PURCHASES_PAGE_TEMPLATE % self.stock_symbol,
        )
        soup = BeautifulSoup(resp.text, "lxml")
        tables = soup.select("table.yfnc_tableout1")
        if len(tables) < 3:
            _PLAIN_ERROR_LOGGER.error("No insider purchases available")
            return 1

        insider_history_table = tables[2]

        headers = []
        rows = []
        for i, tr in enumerate(insider_history_table.select("tr table tr")):
            if i == 0:
                # process headers
                for th in tr.select("th"):
                    headers.append(th.get_text())
            else:
                # process data
                rows.append([td.get_text() for td in tr.select("td")])
        consoleutil.DataPrinter(
            rows,
            headers=headers,
            print_func=_PLAIN_LOGGER.info,
        ).print_result(consoleutil.DataPrinter.PRINT_STYLE_NICETABLE)


def parse_args(cmd_args):
    description = __doc__.split("Copyright 2014")[0].strip()

    parser = argparse.ArgumentParser(
        description=description,
        formatter_class=argparse.RawDescriptionHelpFormatter,
    )
    parser.add_argument(
        "--debug",
        action="store_true",
    )

    parser.add_argument(
        "--fundamentals",
        action="store_true",
        help="Print fundamentals data",
    )

    parser.add_argument(
        "--insider-purchases",
        action="store_true",
        help="Print insider purchases",
    )

    parser.add_argument(
        "--history",
        help="Print historical stock quotes",
        action="store_true",
    )

    parser.add_argument(
        "--no-price-quote",
        action="store_true",
        help="Not printing price quote of the stock",
    )

    parser.add_argument(
        "-n",
        "--num-of-days",
        help="Number of days to print for historical stock quotes",
        type=int,
        default=30,
    )

    parser.add_argument(
        "-k",
        "--kd-line",
        help="Print values for fast stochastic oscillators along with"
            " historical stock quotes. This option can only be used with"
            " --num-of-days and there are at least 14 historical stock quotes."
            " The period used for %%k is 14, and %%d is 3-period"
            " moving average of %%k.",
        action="store_true",
    )

    parser.add_argument(
        "-r",
        "--rsi",
        help="Print RSI with period of 14 days. Also print the RSI that"
            " includes today (so a total of 15 data points)",
        action="store_true",
    )

    parser.add_argument("stock_symbol", nargs="+")

    args = parser.parse_args(cmd_args)
    return args


def main():
    global _PLAIN_LOGGER, _PLAIN_ERROR_LOGGER

    args = parse_args(sys.argv[1:])

    loggingutil.setup_logger(_LOG, debug=args.debug)
    _PLAIN_LOGGER = loggingutil.create_plain_logger("PLAIN")
    _PLAIN_ERROR_LOGGER = loggingutil.create_plain_logger("PLAIN_ERROR", stdout=False)

    for stock_symbol in args.stock_symbol:
        app = StockApp(
            stock_symbol,
            print_history=args.history,
            print_kd=args.kd_line,
            print_rsi=args.rsi,
            print_price_quote=not args.no_price_quote,
            print_fundamentals=args.fundamentals,
            num_of_days_for_history=args.num_of_days,
            print_insider_purchases=args.insider_purchases,
        )
        app.run()


if __name__ == '__main__':
    main()
