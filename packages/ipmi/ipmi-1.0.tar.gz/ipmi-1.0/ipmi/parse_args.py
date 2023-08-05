#!/usr/bin/env python
# coding: utf-8

import argparse
from const import VERSION, EPILOG


def parse_args():
    parser = argparse.ArgumentParser(description="FreeIPMI python wrapper", epilog=EPILOG)

    parser.add_argument("-H", "--hostname", type=str, default="localhost", metavar="HOSTNAME", help="""
        hostname or IP of the IPMI interface.
        For \"-H localhost\" or if no host is specified (local computer) the Nagios/Icinga user must be allowed to run ipmimonitoring/ipmi-sensors/ipmi-sel/[ipmi-fru] with root privileges or via sudo (ipmimonitoring/ipmi-sensors/ipmi-sel/[ipmi-fru] must be able to access the IPMI devices via the IPMI system interface).
    """)
    parser.add_argument("-F", "--credential-file", type=argparse.FileType("r"), help="""
        path to the FreeIPMI configuration file.
        Only neccessary for communication via network.
        Not neccessary for access via IPMI system interface (\"-H localhost\").
        It should contain IPMI username, IPMI password, and IPMI privilege-level,
        for example:
          username monitoring
          password yourpassword
          privilege-level user
        As alternative you can use -U/-P/-L instead (see below).
    """)
    parser.add_argument("-U", "--username", type=str, help="username")
    parser.add_argument("-P", "--password", type=str, help="password")
    parser.add_argument("-L", "--previlege", type=str, default="user", help="""
       previlege
       IPMI username, IPMI password and IPMI privilege level, provided as
       parameters and not by a FreeIPMI configuration file. Useful for RHEL/
       Centos 5.* with FreeIPMI 0.5.1 (this elder FreeIPMI version does not
       support config files).
       Warning: with this method the password is visible in the process list.
                So whenever possible use a FreeIPMI confiugration file instead.
    """)

    parser.add_argument("--nosudo", action="store_true", help="turn off sudo usage on localhost or if ipmi host is ommited")

    parser.add_argument("-r", "--record-ids", type=str, help="""
        Specify sensors to show by record id. Multiple record ids can be separated by commas or spaces. If both --record-ids and --sensor-types  are
        specified,  --record-ids  takes  precedence. A special command line record id of "all", will indicate all record ids should be shown (may be
        useful for overriding configured defaults).
    """)
    parser.add_argument("-R", "--exclude-record-ids", type=str, help="""
        Specify sensors to not show by record id. Multiple record ids can be separated by commas or spaces. A special  command  line  record  id  of
        "none", will indicate no record ids should be excluded (may be useful for overriding configured defaults).
    """)

    parser.add_argument("-t", "--sensor-types", nargs="*", default=[], help="""
        limit sensors to query based on IPMI sensor type.
        Examples for IPMI sensor types are 'Fan', 'Temperature', 'Voltage', ...
        See the output of the FreeIPMI command 'ipmi-sensors -L' and chapter
        '42.2 Sensor Type Codes and Data' of the IPMI 2.0 spec for a full list
        of possible sensor types. You can also find the full list of possible
        sensor types at https://www.thomas-krenn.com/en/wiki/IPMI_Sensor_Types
        The available types depend on your particular server and the available
        sensors there.
    """)
    parser.add_argument("-T", "--exclude-sensor-types", nargs="*", default=[], help="""
       exclude sensors based on IPMI sensor type.
       Multiple sensor types can be specified as a comma-separated list.
    """)

    parser.add_argument("-B", "--compat", action="store_true", help="""
       backward compatibility mode for FreeIPMI 0.5.* (this omits the FreeIPMI
       caching options --quiet-cache and --sdr-cache-recreate)
    """)

    parser.add_argument("-OPT", "--options", nargs="*", default=[], help="free ipmi options")
    parser.add_argument("-D", "--lan-version", action="store_true", help="""
       change the protocol LAN version. Normally LAN_2_0 is used as protocol
       version if not overwritten with this option. Use 'default' here if you
       don't want to use LAN_2_0.
       """)
    parser.add_argument("--no-thresholds", action="store_true", help="turn off performance data thresholds from output-sensor-thresholds.")

    parser.add_argument("--record-delimiter", type=str, default="\n", help="Delimiter of records")
    parser.add_argument("--show-header", action="store_true", help="show header of sensor results")
    parser.add_argument("--sensor-name", type=str, help="Show specific sensors by record name.")
    parser.add_argument("--list-sensor-types", action="store_true", help="List sensor types.")

    parser.add_argument("-V", "--version", action="version", version=VERSION)

    args = parser.parse_args()
    return args
