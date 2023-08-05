# ipmi_tool - NetXMS plugin to check IPMI sensors

## Requirements
* FreeIPMI version 0.5.1 or newer

## Installation hints
* ```apt-get install freeipmi```
* ```pip install ipmi==0.9```
* ```ipmi_tool -H localhost -U username -P password -L user```

## Notes on ipmi-sel
If you want to clear the ipmi system event log, pleas use:
* /usr/sbin/ipmi-sel -h $IP -u ADMIN -p $PW -l ADMIN --clear

## Get same results with NetXMS
- default beheaviour

    ```
    ipmi_tool -H hostname -U username -P password -L user

    4;CPU1 Temp;Temperature;Nominal;'OK';37.00;C;0.00;0.00;80.00;85.00
    71;CPU2 Temp;Temperature;Nominal;'OK';46.00;C;0.00;0.00;80.00;85.00
    138;PCH Temp;Temperature;Nominal;'OK';37.00;C;-8.00;-5.00;90.00;95.00
    205;System Temp;Temperature;Nominal;'OK';25.00;C;-7.00;-5.00;80.00;85.00
    ```
- show headers

    ```
    ipmi_tool -H hostname -U username -P password -L user --show-header

    ID;Name;Type;Status;Event;Reading;Unit;LowCT;Low NC;High NC;High CT
    4;CPU1 Temp;Temperature;Nominal;'OK';38.00;C;0.00;0.00;80.00;85.00
    71;CPU2 Temp;Temperature;Nominal;'OK';47.00;C;0.00;0.00;80.00;85.00
    138;PCH Temp;Temperature;Nominal;'OK';37.00;C;-8.00;-5.00;90.00;95.00
    ```

- list all sensor type and name

    ```
    ipmi_tool -H hostname -U username -P password -L user --list-sensor-types --show-header

    Type;Name
    Temperature;CPU1 Temp
    Temperature;CPU2 Temp
    Temperature;PCH Temp
    Temperature;System Temp
    ```

- filter results by sensor name

    ```
    ipmi_tool -H hostname -U username -P password -L user --show-header --sensor-name "CPU1 Temp"

    ID;Name;Type;Status;Event;Reading;Unit;LowCT;Low NC;High NC;High CT
    4;CPU1 Temp;Temperature;Nominal;'OK';37.00;C;0.00;0.00;80.00;85.00
    ```

- filter results by sensor type

    ```
    ipmi_tool -H hostname -U username -P password -L user --show-header --sensor-type Voltage

    ID;Name;Type;Status;Event;Reading;Unit;LowCT;Low NC;High NC;High CT
    2416;12V;Voltage;Nominal;'OK';12.00;V;10.30;10.74;12.95;13.26
    2483;5VCC;Voltage;Nominal;'OK';4.95;V;4.30;4.48;5.39;5.55
    2550;3.3VCC;Voltage;Nominal;'OK';3.30;V;2.82;2.96;3.55;3.66
    2617;VBAT;Voltage;Nominal;'OK';3.10;V;2.48;2.58;3.49;3.60
    2684;Vcpu1;Voltage;Nominal;'OK';1.81;V;1.26;1.40;1.90;2.09
    2751;Vcpu2;Voltage;Nominal;'OK';1.81;V;1.26;1.40;1.90;2.09
    ```

    ```
    ipmi_tool -H hostname -U username -P password -L user --show-header --exlude-sensor-type Voltage,Temperature,Fan

    ID;Name;Type;Status;Event;Reading;Unit;LowCT;Low NC;High NC;High CT
    3421;Chassis Intru;Physical Security;Nominal;'OK';N/A;N/A;N/A;N/A;N/A;N/A
    3957;PS1 Status;Power Supply;Nominal;'Presence detected';N/A;N/A;N/A;N/A;N/A;N/A
    4024;PS2 Status;Power Supply;Nominal;'Presence detected';N/A;N/A;N/A;N/A;N/A;N/A
    ```

- filter results by sensor id

    ```
    ipmi_tool -H hostname -U username -P password -L user --show-header --record-id 3354

    ID;Name;Type;Status;Event;Reading;Unit;LowCT;Low NC;High NC;High CT
    3354;1.05V PCH;Voltage;Nominal;'OK';1.05;V;0.90;0.94;1.19;1.22
    ```

    ```
    ipmi_tool -H hostname -U username -P password -L user --show-header --exclude-record-id 1,2,3,4

    ID;Name;Type;Status;Event;Reading;Unit;LowCT;Low NC;High NC;High CT
    3354;1.05V PCH;Voltage;Nominal;'OK';1.05;V;0.90;0.94;1.19;1.22
    ```

- hide thresholds

    ```
    ipmi_tool -H hostname -U username -P password -L user --no-threshold

    ID;Name;Type;Status;Event;Reading;Unit
    3354;1.05V PCH;Voltage;Nominal;'OK';1.05;V
    ```

- set output records delimiter

    ```
    ipmi_tool -H hostname -U username -P password -L user --no-threshold --record-delimiter "|"

    ID;Name;Type;Status;Event;Reading;Unit|3354;1.05V PCH;Voltage;Nominal;'OK';1.05;V
    ```

## License
Copyright (C) 2009-2016 Thomas-Krenn.AG,
additional contributors see changelog.txt

This program is free software; you can redistribute it and/or modify it under
the terms of the GNU General Public License as published by the Free Software
Foundation; either version 3 of the License, or (at your option) any later
version.
 
This program is distributed in the hope that it will be useful, but WITHOUT
ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
FOR A PARTICULAR PURPOSE. See the GNU General Public License for more
details.
 
You should have received a copy of the GNU General Public License along with
this program; if not, see <http://www.gnu.org/licenses/>.
