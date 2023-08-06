# django-boxed-alerts

## What does it do?

Adds a whole user alerts/notification system to your django website. Provides the ability
for other apps to create 'alert.py' plugin files within themselves which create
subscription end points that users can use.

Users are also afforded many options that you would expect with subscription
systems. Such as email batching, and subscribing to singular or all signals.

## Installation

```
pip install django-boxed-alerts
```

Add the plugin to your site's settings.py::

```
INSTALLED_APPS = (
  ...
  'alerts',
  ...
)
```

## Issues

Please submit issues and merge requests at GitLab issues tracker: https://gitlab.com/doctormo/django-boxed-alerts/issues/.

