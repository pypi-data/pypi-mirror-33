# pyqualys


pyqualys is simple, easy python client library for Qualys users.

Currently this is in working progress, but there are few features are work (Check TODO).

Install
-----------
```
$ git clone https://github.com/Amitgb14/pyqualys.git
$ cd pyqualys
$ python setup.py install

or

$ pip install pyqualys
```


Example
-----------
* Add Asset
```
# -*- coding: utf-8 -*-
import pyqualys

qualys = pyqualys.QualysAPI(username="admin",
                         password="admin",
                         host="https://qualys.com/")

service = qualys.service("vulnerability")
# Get response in json format, default is xml
service.FORMAT = "json"
asset = service.add_asset(title="myLinux", ips="10.10.10.1")
print("Response", asset)
```
More example in main.py and example/ dir
