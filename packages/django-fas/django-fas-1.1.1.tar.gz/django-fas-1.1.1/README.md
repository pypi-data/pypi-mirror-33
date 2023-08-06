# django-fas

Django auth backend for FAS (Fedora Accounts System)

Installation
------------

Setup **AUTHENTICATION_BACKENDS** in your **settings.py**:

```
AUTHENTICATION_BACKENDS = (
    'fas.backend.FasBackend',
)
```

Add **fas.urls** in your **urls.py**:

```
urlpatterns = patterns('',
    ...
    url('', include('fas.urls')),
    ...
)
```
