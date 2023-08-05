#!/usr/bin/env python
# coding: utf-8

from const import HDRMAP


def ipmi_sensor_netxms_format(
        doc, record_delimiter, show_header=False,
        filter_thresholds=False, sensor_name=None, list_sensor_types=False):
    """
    translate the header and extract the doc into dict
    ordering: reading, lower nc, upper nc, lower c, upper c
    """
    doc_by_row = doc.split("\n")
    header = doc_by_row[0]
    body = doc_by_row[1:]

    origin_header_list = map(lambda i: i.strip(), header.split("|"))
    header_list = [HDRMAP.get(h) for h in origin_header_list]

    result_dict = []
    for row in body:
        if not row:
            continue

        row_fields = map(lambda i: i.strip(), row.split("|"))
        row_ret = {
            header_list[i]: row_fields[i]
            for i in range(len(header_list))
        }
        # if row_ret["reading"] != "N/A":
        result_dict.append(row_ret)

    body = []
    for row in result_dict:
        if sensor_name:
            # filter sensor name
            if sensor_name != row["name"]:
                continue
        if filter_thresholds:
            body_line = ";".join([
                row["id"], row["name"], row["type"], row["state"],
                row["event"], row["reading"], row["units"],
            ])
        elif list_sensor_types:
            body_line = ";".join([row["type"], row["name"]])
        else:
            body_line = ";".join([
                row["id"], row["name"], row["type"], row["state"],
                row["event"], row["reading"], row["units"],
                row["lowerC"], row["lowerNC"], row["upperNC"], row["upperC"],
            ])
        body.append(body_line)

    if show_header:
        if filter_thresholds:
            header = ";".join([
                "ID", "Name", "Type", "Status", "Event", "Reading", "Unit",
            ])
        elif list_sensor_types:
            header = ";".join([
                "Type", "Name",
            ])
        else:
            header = ";".join([
                "ID", "Name", "Type", "Status", "Event", "Reading", "Unit",
                "LowCT", "Low NC", "High NC", "High CT",
            ])
        body.insert(0, header)

    return record_delimiter.join(body)
