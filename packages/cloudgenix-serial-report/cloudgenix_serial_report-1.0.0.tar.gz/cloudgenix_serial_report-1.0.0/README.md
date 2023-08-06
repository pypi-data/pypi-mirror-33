CloudGenix Serial Report
--------
Utility to dump all CloudGenix network serial information to an .XLSX file

#### Requirements
* Active CloudGenix Account
* Python >= 2.7 or >=3.6
* Python modules:
    * cloudgenix >= 5.0.1b1 - <https://github.com/CloudGenix/sdk-python>
    * cloudgenix_idname >= 1.2.0 - <https://github.com/ebob9/cloudgenix-idname>
    * openpyxl >= 2.5.4 - <https://bitbucket.org/openpyxl/openpyxl>

#### License
MIT

#### Usage Example:
```bash
edwards-mbp-pro:Desktop aaron$ serial_report
CloudGenix Serial Report v5.0.1b1 (https://api-test.elcapitan.cloudgenix.com)

login: aaron@cloudgenix.com
Password: 
Building ID->Name lookup table.
Querying APIs.
Parsing Responses.
Building Reports.
edwards-mbp-pro:Desktop aaron$ 
```

#### Version
Version | Changes
------- | --------
**1.0.0**| Initial Release.