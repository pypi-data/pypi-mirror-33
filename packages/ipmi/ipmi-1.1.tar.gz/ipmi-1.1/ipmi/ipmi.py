#!/usr/bin/env python
# coding: utf-8

"""
migrate from check_ipmi_sensor

    1. get the user input
    2. show the parameter information
    3. check if ipmi tools exist
    4. excute it and get result
    5. format the result and give it to user
"""

from os import path as os_path

from format_func import ipmi_sensor_netxms_format
from parse_args import parse_args
from utils import get_ipmimonitoring_path, get_ipmi_version, check_thresholds
from utils import Command


def main():
    args = parse_args()

    use_sudo = None

    if args.nosudo:
        use_sudo = False

    base_command = [get_ipmimonitoring_path()]

    base_command.append("--hostname")
    base_command.append(args.hostname)

    if args.credential_file:
        if not os_path.isfile(args.credential_file):
            assert False, "credential file doesn't exist"
        base_command.append("--config-file")
        base_command.append(args.credential_file)
    elif args.username and args.password and args.previlege:
        base_command.append("--username")
        base_command.append(args.username)
        base_command.append("--password")
        base_command.append(args.password)
        base_command.append("--privilege-level")
        base_command.append(args.previlege)

    # If host is omitted localhost is assumed, if not turned off sudo is used
    if args.hostname == "localhost" and use_sudo is None:
        base_command.insert(0, "sudo")

    if args.record_ids:
        base_command.append('--record-ids={}'.format(args.record_ids))
    if args.exclude_record_ids:
        base_command.append('--exclude-record-ids={}'.format(args.exclude_record_ids))

    if args.sensor_types:
        base_command.append("--sensor-types")
        base_command.append(",".join(args.sensor_types))

    if args.exclude_sensor_types:
        base_command.append("--exclude-sensor-types")
        base_command.append(",".join(args.exclude_sensor_types))

    if not args.compat:
        base_command.append("--quiet-cache")
        base_command.append("--sdr-cache-recreate")

    ipmi_version = get_ipmi_version()
    # since version 0.8 it is necessary to add the legacy option
    if ipmi_version[0] > 0 or ipmi_version[0] == 0 and ipmi_version[1] > 7:
        base_command.append("--interpret-oem-data")

    ipmi_sensors = False
    if ipmi_version[0] == 0 and ipmi_version[1] > 7 and "legacy-output" not in args.options:
        base_command.append("--legacy-output")
    if ipmi_version[0] > 0 and (not args.options or "lagacy-output" not in args.options):
        base_command[0] = base_command[0].replace("monitoring", "-sensors")
        ipmi_sensors = True

    if ipmi_sensors:
        base_command.append("--output-sensor-state")
        base_command.append("--ignore-not-available-sensors")
        base_command.append("--ignore-unrecognized-events")

    lan_version = ""
    if not args.lan_version:
        lan_version = "LAN_2_0"
    if lan_version != "default" and args.hostname != "localhost":
        base_command.append("--driver-type={}".format(lan_version))

    use_thresholds = check_thresholds()
    filter_thresholds = False
    if use_thresholds:
        base_command.append('--output-sensor-thresholds')
    if args.no_thresholds:
        # remove all the thresholds
        filter_thresholds = True

    ret = Command(base_command, use_sudo).call()
    format_params = {
        "doc": ret,
        "record_delimiter": args.record_delimiter,
        "filter_thresholds": filter_thresholds,
    }
    if args.show_header:
        format_params["show_header"] = True
    if args.sensor_name:
        format_params["sensor_name"] = args.sensor_name
    if args.filter_by_headers:
        format_params["filter_by_headers"] = args.filter_by_headers
    elif args.list_sensor_types:
        format_params["list_sensor_types"] = True

    print ipmi_sensor_netxms_format(**format_params)


if __name__ == "__main__":
    main()
