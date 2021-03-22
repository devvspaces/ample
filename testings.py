# import requests

# req = requests.get('http://127.0.0.1:5000')
# print(req.content)

import datetime
import pytz

import math

now = pytz.utc.localize(datetime.datetime.now())

# x = datetime.datetime.strptime('', '%Y-%m-%dT%H:%M:%S%z')
# print(dir(math))
# print(fabs((x-now).days))
print('{} is a number'.format(now))