import argparse
import sys
import time

import requests
from dateparser import parse
from tools import resultview
from dashbase.client import Client
from dashbase.request import QueryRequest

from utils.json import decode_json
from utils.parser import ConfigParser

CONFIG_PATH = "~/.dashbase/dtail.yml"

parser = argparse.ArgumentParser(description='dtail for Dashbase')
parser.add_argument("-c", "--count", type=int, default=10, help="number of lines to return")
parser.add_argument("-n", "--names", type=str, default=None, help="table names, delimit by comma")
parser.add_argument("-a", "--addr", type=str, default=None, help="Log address, e.g. host:port")
parser.add_argument("-q", "--query", type=str, default=None, help="query string")
parser.add_argument("-s", "--stream", type=bool, default=False, help="streaming mode")
parser.add_argument("-d", "--delay", type=int, default=5, help="delay in seconds in streaming mode")
parser.add_argument("-f", "--fields", type=str, default=None, help="fields to display")
parser.add_argument("-r", "--hideraw", type=bool, default=False, help="hide raw data")
parser.add_argument("--debug", type=bool, default=False, help="debug mode")
parser.add_argument("-t", "--time", type=str, default="5 min ago",
                    help="time filter, e.g. May 20 2017 10:11:13,10 min ago")


# parse time
# todo: clean up this function
def parse_time(args):
    if "," not in args.time:
        t1 = parse(args.time)
        if t1 is None:
            sys.exit("unable parse time: " + args.time)
        t2 = None
    else:
        s1, s2 = args.time.split(",", 1)
        t1 = parse(s1)
        if t1 is None:
            sys.exit("unable parse time: " + s1)
        t2 = parse(s2)
        if t2 is None:
            sys.exit("unable parse time: " + s2)

    # set time filter
    time_filter = {}
    if t1 is not None:
        time_filter["startTimeInSec"] = time.mktime(t1.timetuple())
    if t2 is not None:
        time_filter["endTimeInSec"] = time.mktime(t2.timetuple())
    return time_filter


def main():
    config = ConfigParser(parser=parser, config_file=CONFIG_PATH)
    args = config.get_args()
    if args.addr is None:
        parser.print_usage()
        print("dtail: error: argument -a/--addr is required")
        print("or you can edit config file at: {}".format(CONFIG_PATH))
        print("example: ")
        print("addr: staging.dashbase.io:9876")
        print("count: 10")
        return

    client = Client(host=args.addr, get_local_token=True)

    request = QueryRequest(
        disable_highlight=True,
        num=args.count,
        query=args.query
    )

    request.table = ["*"]
    if args.names:
        request.table = args.names.split(",")

    # parse fields
    request.fields = ["*"]
    if args.fields:
        request.fields = args.fields.split(",")

    request.timeRangeFilter = parse_time(args)

    if args.debug:
        print(request.to_dict())

    if args.stream:
        try:
            while True:
                try:
                    res = client.query(request)
                    resultview.print_result(res, True, not args.hideraw, True)
                    # resultview.print_search_stats(0, result)
                    if res.startId:
                        request.endId = res.startId
                except requests.HTTPError as e:
                    print("problem executing query, will try again" + str(e))
                time.sleep(args.delay)
        except KeyboardInterrupt:
            print("Goodbye!")
    else:
        res = client.query(request)
        resultview.print_result(res, True, not args.hideraw, True)


if __name__ == '__main__':
    main()