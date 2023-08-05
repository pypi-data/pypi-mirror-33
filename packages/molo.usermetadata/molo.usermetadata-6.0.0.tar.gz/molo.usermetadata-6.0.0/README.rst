Molo User Metadata
==================

.. image:: https://travis-ci.org/praekelt/molo.usermetadata.svg?branch=develop
    :target: https://travis-ci.org/praekelt/molo.usermetadata
    :alt: Continuous Integration

.. image:: https://coveralls.io/repos/praekelt/molo.usermetadata/badge.png?branch=develop
    :target: https://coveralls.io/r/praekelt/molo.usermetadata?branch=develop
    :alt: Code Coverage

Provides code to help with User metadata in a project using the Molo code base.

.. Note:: This library does not provide a Django user model, it provides a
          metadata model that can be attached to a user. Our experience is
          that custom User models in Django add all sorts of unpleasantries
          when using migrations.

Installation::

   pip install molo.usermetadata


In your app settings::

   INSTALLED_APPS = (
      'molo.usermetadata',
   )

   MIDDLEWARE = (
      'molo.usermetadata.middleware.PeronsaMiddleware'
   )

In your app urls.py::

   urlpatterns += patterns('',
        url(r'^meta/', include('molo.usermetadata.urls', namespace='molo.usermetadata', app_name='molo.usermetadata')),
   )

Note::

   In order for the personae to be activated, choose activate under wagtail settings > personae settings

Google Analytics
----------------

In order for GA to pick up persona data you need to add the following to your base.html

At the top of the template you need to load the persona tag::

    {% load persona_tags %}

In your GTM block add the following to get the persona value::

    {% persona_selected as persona_selected_value %}

In your <noscript> tag add the following to src in order to add the persona to the data layer when JS is not enabled::

    {% if persona_selected_value%}&persona={{ persona_selected_value }}&event=persona{% endif %}

At the bottom of your tag manager block add the following in order to add the persona to the data layer when JS is enabled::

    {% if persona_selected_value %}
      <script type="text/javascript">
        dataLayer.push({'persona': '{{ persona_selected_value }}', 'event': 'persona'});
      </script>
    {% endif %}
