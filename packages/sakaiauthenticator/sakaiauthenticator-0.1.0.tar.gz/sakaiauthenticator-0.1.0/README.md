# SakaiAuthenticator

This is an authentication backend for Django that uses
[Sakai](https://sakaiproject.org/) to authenticate users. They are valid users
if their username and password match and (optionally) if they are a part of a
required site.


# Usage

In `settings.py` of your Django application, add the following:

```python
INSTALLED_APPS = [
    'sakaiauthenticator',
    ...
]

AUTHENTICATION_BACKENDS = [
    'sakaiauthenticator.sakaiauthenticator.SakaiAuthenticator',
    ...
]
SAKAI_URL = 'your.sakai.site';
USE_SAKAI_SITE = True                 # To enable site restricted authentication
SAKAI_SITE_URL = 'your_sakai_site_id'; # To enable site restricted authentication
```
# Notes
The membership API endpoint is currently only in the development version of
SakaiPy. Until the next release, SakaiPy must be installed from
[git](https://github.com/willkara/SakaiPy)
