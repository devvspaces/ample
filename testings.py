# import requests

# req = requests.get('http://127.0.0.1:5000')
# print(req.content)

import datetime
import pytz

import math

now = pytz.utc.localize(datetime.datetime.now())

x = datetime.datetime.strptime('2020-06-30T19:00:00+0200', '%Y-%m-%dT%H:%M:%S%z')
print(dir(math))
print(fabs((x-now).days))