# django-cmsplugin-alerts

## What does it do?

Adds a alert/notification subscription option to the cms toolbar and then
sends an alert to any subscribed user using the django-notification alerts
package.

This requires that you're already using the `django-boxed-alerts` package in
your project.

Will optionally combine with `cmsplugin-diff` to to add more information to the
emails and notification messages sent out. This package is designed to be used
with this extra information.

## Installation

```
pip install cmsplugin-alerts
```

Add the plugin to your site's settings.py::

```
INSTALLED_APPS = (
  ...
  'alerts',
  'cmsplugin_diff',
  'cmsplugin_alerts',
  ...
)
```

## Issues

Please submit issues and merge requests at GitLab issues tracker: https://gitlab.com/doctormo/django-cmsplugin-alerts/issues/.

