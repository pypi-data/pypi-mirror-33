<!--description: A python library to interact with the name.com api. -->
[![PyPI](https://img.shields.io/pypi/v/pynamedotcom.svg)](https://pypi.python.org/pypi/pynamedotcom)
[![Build Status](https://travis-ci.org/benmaddison/pynamedotcom.svg?branch=master)](https://travis-ci.org/benmaddison/pynamedotcom)
[![codecov](https://codecov.io/gh/benmaddison/pynamedotcom/branch/master/graph/badge.svg)](https://codecov.io/gh/benmaddison/pynamedotcom)
[![Requirements Status](https://requires.io/github/benmaddison/pynamedotcom/requirements.svg?branch=master)](https://requires.io/github/benmaddison/pynamedotcom/requirements/?branch=master)

# pynamedotcom

A python library to interact with the name.com api

## Installation

```bash
$ pip install pynamedotcom
```

## API Usage

```python
>>> # read authentication details
...
>>> import json
>>> with open("tests/auth.json") as f:
...     auth = json.load(f)
...
>>> # initialise api
...
>>> import pynamedotcom
>>> host = "api.dev.name.com"
>>> # get domains
...
>>> with pynamedotcom.API(host=host, **auth) as api:
...     for domain_name in api.domains:
...         print(domain_name)
...
wolcomm.net
maddison.family
>>>
>>> # fetch domain object
...
>>> with pynamedotcom.API(host=host, **auth) as api:
...     domain = api.domain(name="maddison.family")
...
>>> domain
Domain(maddison.family)
>>>
>>> # get/set domain properties
...
>>> domain.name
u'maddison.family'
>>> domain.nameservers
[u'ns1.example.com', u'ns2.example.com']
>>> domain.nameservers = ['foo.example.org', 'bar.example.org']
>>> domain.nameservers
[u'foo.example.org', u'bar.example.org']
```

## CLI Usage

See `namedotcom --help`
