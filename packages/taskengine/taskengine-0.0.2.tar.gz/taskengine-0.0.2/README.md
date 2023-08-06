# ProcessEngineV2

## Overview

* A process engine instance will have a number of registered services.
* A registered service exposes available tasks in a predictable manner
* One can then build processes in the Process Engine which combine tasks from various registered services
* Profit

## Getting started:

### Setting up the Process Engine:

**Running with Docker**

### Exposing tasks on a service

#### DRF Integration

> We provide a Django Rest Framework library which makes registering a service plug and play

##### On your service:

```
pip install taskengine
```

Add to installed apps: `taskengine`

Add to urls:

```
```

In `settings.py` inform the task engine which modules it can expose:

```
# a list of modules containing tasks that
# can be exposed
ALLOWED_TASK_MODULES = {
    'api.tasks'
}
```

Optional: Set an API KEY this is required to access this endpoint:

```
TASKENGINE_KEY = 'A6568BC7-6AA1-40D9-AD80-E23E8D13B9BF'
```

****


**Registering the API**

### The UI

...