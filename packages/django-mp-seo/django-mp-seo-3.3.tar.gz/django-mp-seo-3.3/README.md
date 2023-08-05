# MP-SEO

Django SEO app.

### Installation

Install with pip:

```
pip install django-mp-seo
```

Add seo to settings.py:

```
INSTALLED_APPS = [
    'seo'
]
```

Run migrations:

```
$ python manage.py migrate
```

### Template tags

To get page meta data in template you should load 'seo' tags and add 'get_page_meta' template tag into your template. 
Examples:

```
{% load seo %}
{% get_page_meta as PAGE_META %}

<title>{% block meta_title %}{{ PAGE_META.printable_title }}{% endblock %}</title>

<meta name="keywords" content="{% block meta_keywords %}{{ PAGE_META.printable_keywords }}{% endblock %}">

<meta name="description" content="{% block meta_description %}{{ PAGE_META.printable_description }}{% endblock %}">

<meta name="robots" content="{% block meta_robots %}{{ PAGE_META.robots }}{% endblock %}" />
```
