# django-tls-middleware
[![Build Status](https://travis-ci.org/sekomy/django-tls-middleware.svg?branch=master)](https://travis-ci.org/sekomy/django-tls-middleware)

Stores the current request in [Thread Local Storage](https://en.wikipedia.org/wiki/Thread-local_storage).
### Installation
```bash
    pip install django-tls-middleware
```

### Configuration
```bash
    # settings.py
    MIDDLEWARE = [
        ...
        'tls_middleware.TLSMiddleware',
   ]
```

### Usage
```bash
from tls_middleware import get_request
request = get_request()
# do something useful with current request object
```
