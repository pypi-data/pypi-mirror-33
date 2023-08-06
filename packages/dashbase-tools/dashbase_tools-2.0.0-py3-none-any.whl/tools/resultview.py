from __future__ import print_function

import datetime
import json

from terminaltables import AsciiTable
from dashbase.response import Response, InfoResponse, ClusterOverviewResponse, ClusterInfo
from colorama import init
from pygments import highlight, lexers, formatters
from termcolor import colored
from utils import textwrap

init()


def print_json(result):
    formatted_json = json.dumps(result, indent=4, sort_keys=True)
    colorful_json = highlight(formatted_json, lexers.JsonLexer(), formatters.TerminalFormatter())
    print(colorful_json)


def hms_string(sec_elapsed):
    h = int(sec_elapsed / (60 * 60))
    m = int((sec_elapsed % (60 * 60)) / 60)
    s = sec_elapsed % 60.
    return "{}:{:>02}:{:>05.2f}".format(h, m, s)


def sizeof_fmt(num, suffix='B'):
    for unit in ['', 'Ki', 'Mi', 'Gi', 'Ti', 'Pi', 'Ei', 'Zi']:
        if abs(num) < 1024.0:
            return "%3.1f %s%s" % (num, unit, suffix)
        num /= 1024.0
    return "%.1f %s%s" % (num, 'Yi', suffix)


def format_time_value(time_in_seconds):
    value = datetime.datetime.fromtimestamp(time_in_seconds)
    return value.strftime('%Y-%m-%d %H:%M:%S')


def raw_payload(hit):
    raw = "Not Available"
    payload = hit.get("payload")
    if payload is not None:
        stored = payload.get("stored")
        if stored is not None:
            raw = stored
    return raw.encode('utf-8').strip()


def print_result(response, hide_border_and_title, show_raw, reverse_hits=False):
    if len(response.hits) == 0:
        print("No hits")
        return
    print_hits(response, hide_border_and_title, show_raw, reverse_hits)


def draw_numeric_aggregation(name, numeric, req_agg):
    header_names = ["numRows", "value"]
    data = [header_names]
    title = "{}={}({})".format(name, req_agg["type"], req_agg["col"])
    table = AsciiTable(data, title)
    if numeric is not None:
        num_docs = "{:,}".format(numeric["numDocs"])
        value = "{0:.2f}".format(numeric["value"])
        data.append([num_docs, value])
    return table.table


def print_numeric_aggregation(name, numeric, aggr_req):
    print(draw_numeric_aggregation(name, numeric, aggr_req))


def print_ts_aggregation(name, histograms):
    header_names = ["start", "end", "count"]
    data = [header_names]
    if histograms is not None:
        interval = histograms["bucketSizeInSeconds"]
        title = name + "(interval = {})".format(hms_string(interval))
        table = AsciiTable(data, title)
        buckets = histograms["histogramBuckets"]
        for bucket in buckets:
            start = format_time_value(bucket["timeInSec"])
            end = format_time_value(bucket["timeInSec"] + interval)
            count = "{:,}".format(bucket["count"])
            data_array = [start, end, count]
            data.append(data_array)
    else:
        table = AsciiTable(data, name)
    print(table.table)


def draw_topn_aggregation(name, topn):
    header_names = ["value", "count"]
    data = [header_names]
    if topn is not None:
        col = topn["col"]
        title = name + "(column={})".format(col)
        table = AsciiTable(data, title)
        facets = topn["facets"]
        for facet in facets:
            count = "{:,}".format(facet["count"])
            data.append([facet["value"], count])
    else:
        table = AsciiTable(data, name)
    return table.table


def print_topn_aggregation(name, topn):
    print(draw_topn_aggregation(name, topn))


def draw_agg_resp(agg, sub_req):
    agg_str = None
    if agg is not None:
        agg_type = agg.get("responseType")
        if agg_type is not None:
            if agg_type == "numeric":
                agg_str = draw_numeric_aggregation(agg_type, agg, sub_req)
            elif agg_type == "topn":
                agg_str = draw_topn_aggregation(agg_type, agg)
    return agg_str


def print_tsa_aggregation(name, tsa, sub_req):
    header_names = ["start", "end", "bucket"]
    data = [header_names]
    if tsa is not None:
        interval = tsa.get("bucketSizeInSeconds", 0)
        buckets = tsa.get("buckets", [])
        title = name + "(interval = {})".format(hms_string(interval))
        table = AsciiTable(data, title)
        for bucket in buckets:
            start = format_time_value(bucket["timeInSec"])
            end = format_time_value(bucket["timeInSec"] + interval)
            agg_str = draw_agg_resp(bucket["response"], sub_req)
            if agg_str is None:
                agg_str = "n/a"
            data_array = [start, end, agg_str]
            data.append(data_array)
    else:
        table = AsciiTable(data, name)
    print(table.table)


def print_aggregations(res):
    # type: (Response) -> ()
    for name, agg in res.aggregations.items():
        req_agg = res.request.aggregations.get(name)
        if req_agg and agg:
            agg_type = agg.get("responseType")
            if agg_type == "ts":
                print_ts_aggregation(name, agg)
            elif agg_type == "numeric":
                print_numeric_aggregation(name, agg, req_agg)
            elif agg_type == "topn":
                print_topn_aggregation(name, agg)
            elif agg_type == "tsa":
                sub_req = agg.get("subRequest")
                if sub_req is not None:
                    print_tsa_aggregation(name, agg, sub_req)


def print_time_range(res: Response):
    t1, t2 = None, None
    time_range_filter = res.request.timeRangeFilter
    if time_range_filter is not None:
        t1 = datetime.datetime.fromtimestamp(
            time_range_filter.startTimeInSec
        ).strftime('%Y-%m-%d %H:%M:%S')
        t2 = datetime.datetime.fromtimestamp(
            time_range_filter.endTimeInSec
        ).strftime('%Y-%m-%d %H:%M:%S')
    print("Time range: from {} to {}".format(t1, t2))


def print_debug_info(request):
    debugMap = request.get("debugMap")
    if debugMap is not None:
        header_names = ["name", "value"]
        data = [header_names]
        for field in debugMap:
            debugField = debugMap.get(field)
            if debugField is not None:
                data_array = [field, debugField]
                data.append(data_array)
        table = AsciiTable(data, "debug info")
        print(table.table)


def print_search_stats(client_latency, result):
    latency = result.get("latencyInMillis", 0) / 1000.0
    client_latency = client_latency / 1000.0
    time_string = "(s={0:.2f}, c={1:.2f}) sec".format(latency, client_latency)
    num_docs = result.get("numDocs", 0)
    total_docs = result.get("total_docs", 0)
    use_approximation = result.get("request", {}).get("use_approximation", False)
    return "{:,} rows of {:,}, took: {}, approximation = {}".format(num_docs,
                                                                    total_docs,
                                                                    time_string,
                                                                    use_approximation)


def get_highlight_entity(hit):
    payload = hit.get("payload")
    if payload is None:
        return None
    entities = payload.get("entities", [])
    for entity in entities:
        if 'highlight' in entity:
            return entity["highlight"]
    return None


def get_hl_field_entities(hit, field):
    highlight_entity = get_highlight_entity(hit)
    if highlight_entity:
        fields = highlight_entity.get('fields', {})
        return fields.get(field)
    return None


def get_hl_stored_entities(hit):
    highlight_entity = get_highlight_entity(hit)
    if highlight_entity:
        return highlight_entity.get("stored")
    return None


def get_header(hit):
    headers = ["time"]
    for field in hit.payload.fields:
        if field == "_stored":
            continue
        headers.append(field)
    headers += ["RAW"]
    return headers


def highlight_raw(text, entities, max_width):
    try:
        entity = entities[0]
        if not entity.is_highlight_entity():
            return text
        offset = 0
        for index in entity.highlight.stored:
            start = index.offset
            # add newline char offset
            end = start + index.length
            # add newline char offset
            start += int(start / max_width) + offset
            end += int(end / max_width) + offset
            left = text[:start]
            mid = ""
            for char in text[start:end]:
                if char == "\n":
                    mid += char
                else:
                    mid += colored(char, on_color='on_yellow')
            right = text[end:]
            text = left + mid + right
            offset += len(mid) - (end - start)
        return text

    except IndexError:
        return text


def print_hits(res: Response, hide_border_and_title=False, show_raw=True, reverse=False):
    # import ipdb;ipdb.set_trace()
    if len(res.hits) == 0:
        print("No hits")
        return

    headers = get_header(res.hits[0])
    data = []
    table = AsciiTable(data, "Hits")
    data.append(headers)

    if reverse:
        res.hits = list(reversed(res.hits))

    for hit in res.hits:
        # first add time
        row = [format_time_value(hit.timeInSeconds)]
        fields = hit.payload.fields
        for key in fields:
            if key == "stored":
                continue
            try:
                row.append(fields[key][0])
            except IndexError:
                row.append("n/a")
        data.append(row)

    # table.column_max_width need filled another column
    max_width = table.column_max_width(len(headers) - 1)
    is_fill = True
    if max_width < 30:
        print(colored("Warn: your terminal width not enough, highlight and wrap raw is disable", color="yellow"))
        print()
        is_fill = False
    for idx, hit in enumerate(res.hits):
        if show_raw:
            raw = "Not Available"
            if hit.payload.stored:
                raw = hit.payload.stored
            if is_fill:
                value = textwrap.fill(raw, max_width, drop_whitespace=False)
                value = highlight_raw(value, hit.payload.entities, max_width)
            else:
                value = raw
            data[idx + 1].append(value)

    if hide_border_and_title:
        table.title = None
        table.inner_heading_row_border = False
        table.outer_border = False
        table.inner_column_border = False
        data.pop(0)

    if len(data) > 0:
        # if table.ok:
        print(table.table)
        # else:
        #     print("Error: your terminal width not enough")


def print_schema(name: str, res: InfoResponse):
    if not name:
        name = "__default"
    header_names = ["column", "type"]
    data = [header_names]
    title = "{}:{} rows".format(name, res.numDocs)
    table = AsciiTable(data)
    if not res.schema:
        print("table: {} not found".format(name))
        print("problem fetching schema for table: \"{}\"".format(name))

    for key, value in res.schema.items():
        data.append([key, value])
    print(title)
    print(table.table)


def print_cluster(name, res: ClusterOverviewResponse):
    if name:
        if name not in res.overview:
            print("table: \"" + name + "\" not found.")
            return
        return print_table_info(name, res.overview[name])

    print("tables: [{}]".format(",".join(res.overview.keys())))
    for k, v in res.overview.items():
        print_table_info(k, v)


def print_table_info(name, cluster_info: ClusterInfo):
    metrics = cluster_info.metrics
    metrics_data = [["type", "time unit", "volume"],
                    ["bytes", "per second", sizeof_fmt(metrics.indexing.numBytesPerSecond)],
                    ["bytes", "per day", sizeof_fmt(metrics.indexing.numBytesPerDay)],
                    ["events", "per second", "{:,}".format(metrics.indexing.numEventsPerSecond)],
                    ["events", "per day", "{:,}".format(metrics.indexing.numEventsPerDay)]]

    metrics_table = AsciiTable(metrics_data, name + ": ingestion")
    print(metrics_table.table)
    partitions_data = [["partition", "hosts"]]
    partitions_table = AsciiTable(partitions_data, name + ": partitions")
    for p, host_list in cluster_info.info.items():
        partitions_data.append([p, "\r".join(host_list)])
    print(partitions_table.table)
