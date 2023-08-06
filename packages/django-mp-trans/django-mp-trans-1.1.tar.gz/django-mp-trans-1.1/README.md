# Translation app
This app helps translate admin fields using `django-modeltranslation` and `googletrans`

## Installation
`$ pip install mp-trans`

## Setup
1. Add `trans` and `modeltranslation` to the `INSTALLED_APPS` variable of your project’s `settings.py`
2. Set `IS_ADMIN_FIELDS_TRANSLATION_ENABLED` option to `True` in your `settings.py`
3. Add `url(r'^trans/', include('trans.urls')),` to your `urls.py`

## Admin usage
1. Import `TranslationAdmin` class.
```
from trans.admin import `TranslationAdmin`
```
2. Extend your admin class with `TranslationAdmin`
```
class MyModelAdmin(TranslationAdmin):
	pass
```
