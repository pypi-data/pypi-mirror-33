Introduction
============

statusmessages provides an easy way of handling internationalized status
messages managed via an BrowserRequest adapter storing status messages in
client-side cookies.

It is quite common to write status messages which should be shown to the user
after some action. These messages of course should be internationalized. As
these messages normally are defined in Python code, the common way to i18n-ize
these in Zope is to use zope.i18n Messages. Messages are complex objects
consisting of a translation domain and a default unicode text and might have an
additional mapping dict and a distinct id.

The usual way to provide status messages in CMF/Plone has been to add a
"?portal_status_messages=some%20text" to the URL. While this has some usability
problems it also isn't possible to i18n-ize these in the common way, as the URL
is currently limited to the ASCII charset, but an encoding providing support for
the full unicode range is required.

The solution provided by this module is to store the status messages inside a
cookie. In version 1.x a server side session like storage has been used, but
this turned out not to be caching friendly for the usual web caching strategies.
