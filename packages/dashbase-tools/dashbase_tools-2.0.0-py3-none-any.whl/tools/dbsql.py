from __future__ import print_function

import argparse
import urllib
from cmd import Cmd

import requests
import urllib3
from dashbase.client import Client
from tools import resultview
from utils.json import decode_json


class DashbaseConsole(Cmd):
    """Dashbase Commandline Console"""

    def __init__(self, client: Client, json_out, **kwargs):
        Cmd.__init__(self, **kwargs)
        self.client = client
        self.json_out = json_out

    def handle_exception(self, e):
        print("problem executing query, please try again: " + str(e))

    def do_schema(self, name):
        """shows table schemas"""
        try:
            if not name:
                result = self.client.info()
            else:
                result = self.client.info(names=[name])
        except requests.HTTPError as e:
            self.handle_exception(e)
            return

        if self.json_out:
            resultview.print_json(result.raw_res)
        else:
            resultview.print_schema(name, result)

    def do_table(self, name):
        """show table information"""
        try:
            if not name:
                result = self.client.all_cluster_info()
            else:
                result = self.client.cluster_info(name)

        except requests.HTTPError as e:
            self.handle_exception(e)
            return

        if self.json_out:
            resultview.print_json(result.raw_res)
            return
        if not result.overview:
            print("unable to get table list")
        resultview.print_cluster(name, result)

    def do_debug(self, query):
        sql = "debug " + query
        return self.exec_select(sql)

    def do_select(self, query):
        sql = "select " + query
        return self.exec_select(sql)

    def exec_select(self, sql):
        """runs a dashbase sql"""
        try:
            res = self.client.sql(sql)
        except requests.HTTPError as e:
            self.handle_exception(e)
            return
        if self.json_out:
            resultview.print_json(res.raw_res)
            return
        if res.error:
            print("Error: {}".format(res.error))
        else:
            resultview.print_hits(res)
            resultview.print_aggregations(res)
            resultview.print_time_range(res)
            # resultview.print_search_stats(latency, result)
            # resultview.print_debug_info(result)

    def do_quit(self, _):
        """Exits the program."""
        print("Quitting.")
        return True

    def do_exit(self, _):
        """Exits the program."""
        print("Quitting.")
        return True


def main():
    parser = argparse.ArgumentParser(description='Sql console for Dashbase')
    parser.add_argument("-a", "--address", type=str, required=True, help="Log name, e.g. host:port, required")
    parser.add_argument("-o", "--output", type=str, default=None, help="output format, e.g. json/None, default: None")
    args = parser.parse_args()

    client = Client(host=args.address, get_local_token=True)
    json_out = args.output == "json"
    try:
        console = DashbaseConsole(client, json_out)
        console.prompt = '> '
        console.cmdloop('Starting Dashbase console... Press Ctrl+C or input "exit" to exit!')
    except KeyboardInterrupt:
        print('Goodbye!')


if __name__ == '__main__':
    main()
