# Django ping-me application
 
This app has to be integrated into an existing django website.

The purpose of this application is to establish an HTTP connection with a web server list in order to make availability statistics.

## Quick start

1. Add "ping-me" to your INSTALLED_APPS setting like this:
```
INSTALLED_APPS = [  
    ...  
    'ping_me',  
]
```

2. Include the ping-me URLconf in your project urls.py like this:
```
path('ping-me/', include(('ping_me.urls', 'ping_me'))),
```

3. Run `python manage.py migrate` to create models.

4. Start the development server and visit http://127.0.0.1:8000/ping-me to check if everything is ok.

## Override those ugly templates

You can add a *templates/ping_me* folder in your base application to override default templates.

Have a look on [default templates](https://gitlab.com/aloha68/django-ping-me/tree/master/ping_me/templates/ping_me) to see how to override them.  
Keep in mind that some features (like edit or delete a template) use *bootstrap* popups and AJAX calls.
