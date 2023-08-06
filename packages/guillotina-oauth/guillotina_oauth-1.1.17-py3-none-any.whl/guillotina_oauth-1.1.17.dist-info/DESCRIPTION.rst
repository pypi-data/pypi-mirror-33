.. contents::

GUILLOTINA_OAUTH
================


WARNING: this package requires a working plone.oauth server...


Features
--------

 * There is no persistence information about the user

 * The configuration is global for all application


Configuration
-------------

Generic global configuration on guillotina utilities section:

{
    "applicatoins": ["guillotina_oauth"],
    "auth_token_validators": [
        "guillotina.auth.validators.SaltedHashPasswordValidator",
        "guillotina_oauth.oauth.OAuthJWTValidator"
    ],
    "oauth_settings": {
        "server": "http://localhost/",
        "jwt_secret": "secret",
        "jwt_algorithm": "HS256",
        "client_id": 11,
        "client_password": "secret"
    }
}

1.1.17 (2018-07-10)
-------------------

- add check_scope_id


1.1.16 (2018-06-05)
-------------------

- Release to constrain version of guillotina
  [vangheem]


1.1.15 (2018-05-21)
-------------------

- Make sure to use service token for endpoints that ask for it
  [vangheem]


1.1.14 (2018-05-17)
-------------------

- json handling fixes


1.1.13 (2018-05-17)
-------------------

- better handling of add_scope
  [vangheem]


1.1.12 (2018-05-12)
-------------------

- Add more logging


1.1.11 (2018-05-10)
-------------------

- check_scope_id is a GET


1.1.10 (2018-05-08)
-------------------

- bump


1.1.9 (2018-05-08)
------------------

- Add client_id params to some endpoints
  [vangheem]


1.1.8 (2018-05-07)
------------------

- add data attribute to add_user
  [vangheem]

1.1.8 (2018-05-07)
------------------

- add modify limit


1.1.7 (2018-05-07)
------------------

- get_account_metadata and set_account_metadata methods added
  [vangheem]


1.1.6 (2018-05-04)
------------------

- add add_scope method
  [vangheem]

- add check_scope_id method
  [vangheem]

- get_temp_token works without a container
  [vangheem]


1.1.5 (2018-05-04)
------------------

- Use `permissions` data
  [vangheem]

1.1.4 (2018-04-09)
------------------

- Getting the user with the user bearer token to valide when its not cached
  [ramon]


1.1.3 (2018-03-15)
------------------

- Only use authorization header if provided to get_temp_token
  [vangheem]


1.1.2 (2018-03-15)
------------------

- Be able to provide authorization header to get_temp_token
  [vangheem]


1.1.1 (2018-03-15)
------------------

- Add service_get_user endpoint support
  [vangheem]


1.1.0 (2018-03-14)
------------------

- Upgrade to work with Guillotina 2.4.x
  [vangheem]


1.0.32 (2018-03-07)
-------------------

- Use token for user cache key instead of login
  [vangheem]


1.0.31 (2018-02-20)
-------------------

- Add grant and revoke scope roles method
  [vangheem]


1.0.30 (2018-02-16)
-------------------

- Change default clear value
  [vangheem]


1.0.29 (2018-02-16)
-------------------

- Be able to clear from argument
  [vangheem]


1.0.28 (2018-02-08)
-------------------

- Use send email instead of remind
  [vangheem]


1.0.27 (2018-02-08)
-------------------

- Fix add_user
  [vangheem]


1.0.26 (2018-02-07)
-------------------

- Support websocket tokens
  [vangheem]


1.0.25 (2018-01-24)
-------------------

- Add get_temp_token and retrieve_temp_data methods
  [vangheem]


1.0.24 (2018-01-15)
-------------------

- Send authorization header for `get_user`
  [vangheem]


1.0.23 (2018-01-10)
-------------------

- Store user data on authenticated user object
  [vangheem]


1.0.22 (2017-12-07)
-------------------

- Add get_user and add_user methods to utility
  [vangheem]


1.0.21 (2017-11-08)
-------------------

- Handle CancelledError
  [vangheem]


1.0.20 (2017-11-01)
-------------------

- Fix search_users
  [vangheem]


1.0.19 (2017-09-25)
-------------------

- Cache user object for 1 minute to lay off oauth server
  [vangheem]


1.0.18 (2017-09-15)
-------------------

- Change various logging statements to "debug"
  [vangheem]


1.0.17 (2017-09-08)
-------------------

- Fix release
  [vangheem]


1.0.16 (2017-09-08)
-------------------

- Provide `auto_renew_token` setting to setting--useful in tests
  [vangheem]


1.0.15 (2017-08-09)
-------------------

- Be able to configure timeouts for oauth requests
  [vangheem]


1.0.14 (2017-08-08)
-------------------

- b/w compat OPTIONS call for getting auth code
  [vangheem]


1.0.13 (2017-08-07)
-------------------

- override OPTIONS for @oauthgetcode
  [vangheem]


1.0.12 (2017-08-04)
-------------------

- Detect invalid service tokens and refresh
  [vangheem]


1.0.11 (2017-08-04)
-------------------

- More logging


1.0.10 (2017-08-04)
-------------------

- Log correct service token
  [vangheem]


1.0.9 (2017-08-04)
------------------

- More logging
  [vangheem]


1.0.8 (2017-08-04)
------------------

- Handle errors better on renewing service tokens
  [vangheem]


1.0.7 (2017-07-24)
------------------

- Allow user to validate without any roles from api
  [vangheem]


1.0.6 (2017-07-24)
------------------

- Fix use of OPTIONS for oauth endpoint
  [vangheem]

- make sure POST request pushes variables to oauth endpoint as json data
  [vangheem]


1.0.5 (2017-07-24)
------------------

- @oauthgetcode now works on application root as well as container
  [vangheem]


1.0.4 (2017-06-25)
------------------

- User id on oauth may not be mail
  [bloodbare]

1.0.3 (2017-06-16)
------------------

- Handle oauth errors on connecting to invalid server
  [vangheem]


1.0.2 (2017-06-16)
------------------

- Handle errors when no config is provided
  [vangheem]


1.0.1 (2017-06-15)
------------------

- Do not raise KeyError if user is not found, raise Unauthorized
  [vangheem]


1.0.0 (2017-04-24)
------------------

- initial release


