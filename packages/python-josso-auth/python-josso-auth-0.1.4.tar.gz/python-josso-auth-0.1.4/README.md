# python-josso-auth #

`python-josso-auth` provides a `JOSSOAuth` authentication for `python-social-auth`,
which you can subclass to easily add JOSSO providers as social auth options.

To use, just create a class for your provider which extends `JOSSOAuth` and provide a name and base URL.

```python
from josso.backend import JOSSOAuth

class ExampleJOSSOProvider(JOSSOAuth):
    name = 'example_josso'
    base_url = 'https://example.com/josso/'
```

Now you can include your backend in your settings. For example, with Django:
 ```python
AUTHENTICATION_BACKENS += ('myapp.backends.ExampleJOSSOProvider',)
 ```

## Install ##

```bash
$ pip install python-josso-auth
```
