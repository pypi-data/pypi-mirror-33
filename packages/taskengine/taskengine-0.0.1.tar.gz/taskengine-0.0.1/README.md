Library to handle exposing tasks to a ProcessEngine

## Getting started

```
pip install taskengine
```

**Add to installed apps**

**Confgure your task modules**

In settings.py:
```
INSTALLED_APPS = [
    ..
    'taskengine',
    ..
]
```

**Tell taskengine where to find tasks**

In settings.py:

```
ALLOWED_TASK_MODULES = {
    'taskengine.tasks', # these are default tasks provided by taskengine
    .., # <- your module/s here
}

# optional
TASKENGINE_API_KEY = '...'

```

**Add API to urls**

in urls.py
```
from taskengine.api import router as task_router
..

urlpatterns = [
    ..
    path(r'', include(task_router.urls)),
    ..
]
```

**Register your service**

```
python manage.py register
```


