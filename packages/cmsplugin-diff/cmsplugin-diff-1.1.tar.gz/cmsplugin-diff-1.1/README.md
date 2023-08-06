# django-cmsplugin-diff

## What does it do?

Provides a history of changes, when plugins were edited, by who, when pages
are published and by who. It tracks the languages of each and provides a diff
showing what changed in both a field based view and a body based view.

This plugin is in development and is considered BETA, please test and report issues.

## Demonstration

To set up the demonstration on your local machine, you can::

```
git clone https://github.com/doctormo/django-cmsplugin-diff

cd django-cmsplugin-diff

./setup.py demo
```

Then visit the generated website as instructed.

## Installation

```
pip install cmsplugin-diff
```

Add the plugin to your site's settings.py, making sure it goes BEFORE `cms` or the templates will not over-ride as expected::

```
INSTALLED_APPS = (
  'django.contrib.humanize',
  ...
  'cmsplugin_diff',
  'cms',
  ...
)
```

Add the comment middleware, this allows us to record the user_id and the comment when editing plugins::

```
MIDDLEWARE = [
  ...
  'cmsplugin_diff.middleware.EditCommentMiddleware',
  ...
]
```

Add the urls to your urls.py::

```
urlpatterns += i18n_patterns(
  ...
  url(r'^diff/', include('cmsplugin_diff.urls', namespace='cmsplugin_diff')),
  ...
)
```

## Issues

Please submit issues and merge requests at GitHub issues tracker: https://github.com/doctormo/django-cmsplugin-diff/issues/.

