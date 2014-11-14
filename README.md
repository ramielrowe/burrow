## burrow ##

A simple Python library for interacting with Nest's Mobile API.

Compared to existing clients, burrow offers a better experience for automated
and frequent API calls. This is because it tracks it's access token through
calls and will not re-login each call. Users who make frequent calls should
have their web sessions expire less often and will hopefully not be re-logging
back in each day.


### Installation ###

Burrow is available through pypi:

    pip install burrow

Installing from a git clone

    python setup.py install

### Usage ###

Output stats as json dictionary

    burrow ~/.burrow.json


### Config Sample ###

    {"username": "your@email.com", "password": "your password"}

After first usage, config file will contain additional keys. These include
the access token, userid, and transport url. This is so that the script won't
need to log in each call.
