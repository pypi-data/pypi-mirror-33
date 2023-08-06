# fcredis
[![Build Status](https://travis-ci.com/forever-am/fcredis.svg?branch=master)](https://travis-ci.com/forever-am/fcredis)
[![codecov](https://codecov.io/gh/forever-am/fcredis/branch/master/graph/badge.svg)](https://codecov.io/gh/forever-am/fcredis)
[![Maintainability](https://api.codeclimate.com/v1/badges/223b776a230b67ed426c/maintainability)](https://codeclimate.com/github/forever-am/fcredis/maintainability)

Redis API for user and allocation management

## RedisUsers

An object of `RedisUsers` can be created with an redis `url` and a `salt`, the latter is a password that helps 
to encrypt sensitive fields in the user data in storage and decrypt the sensitive data when reading.

When `salt` is not given, you will store the sensitive data directly into the database. And when you get the data,
you will still have the sensitive fields encrypted. An example of this is as following

```python
import os
import fcredis

users = fcredis.RedisUsers.from_url(os.environ["REDIS_URL"], os.environ.get("REDIS_USERS_SALT"))
users.add(5236871, {"name": "Wang", "kraken_public_api_key": "daeaereq12"})
print(users[5236871])
# {'name': 'Wang', 'kraken_public_api_key': 'daeaereq12'}

users_without_salt = users.RedisUsers.from_url(os.environ["REDIS_URL"])
print(users_without_salt[5236871])
# {'name': 'Wang', 'kraken_public_api_key': '0301688cd6efd8a3084352865ffade534ba3e20c9e3a527b5eb1b57e80c6f802782966ff897ecfe4843b4817d2286a05b570b852ab51d6bde1b4bcd652c6a3d7e9ed8fb54db4ac89597b6df07153001a60f3', 'is_key_encrypted': True}
```

Different types of data start with different prefix, for example, users use the user_id as identifier.
While the real key in the database is with a prefix `USER:`.
You can use the methods `to_json, from_json, to_dict` to convert all the user data into the format you want.

```python
users_without_salt.to_dict()
"""
{
  "USER:5236871": {
    "is_key_encrypted": true,
    "kraken_public_api_key": "0301fe555daf4016bfb1b952f4fb83aeba45c015d9ebb15980ad710bebe8323af24528d25e52c74698560d7c212034e822354500051b66b1e42653bf88bda8f42d3ea3411697809f7a098e19ef427fafb093",
    "name": "Wang"
  }
}
"""
``` 