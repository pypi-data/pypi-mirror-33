Changelog
=========

5.0.3 (2018-06-21)
------------------

Bug fixes:

- Python 3 compatibility fixes.
  [pbauer]


5.0.2 (2018-02-05)
------------------

New features:

- Add Python 2 / 3 compatibility
  [davilima6]


5.0.1 (2017-11-26)
------------------

Bug fixes:

- Fix issue where encoding and decoding of statusmessages into cookie
  raised exception, because of
  ``TypeError: Struct() argument 1 must be string, not unicode``
  [datakurre]


5.0 (2017-08-04)
----------------

Breaking changes:

- Remove python 2.6 (and thus Plone 4.3.x) compatibility.
  [tomgross]

New features:

- Python 3 compatibility
  [tomgross]

Bug fixes:

- Update code to follow Plone styleguide.
  [gforcada]


4.1.2 (2017-02-12)
------------------

Bug fixes:

- Fix deprecated import in test.
  [pbauer]


4.1.1 (2016-08-11)
------------------

Bug fixes:

- Use zope.interface decorator.
  [gforcada]


4.1.0 (2016-05-25)
------------------

New features:

- Convert tests to plone.app.testing.
  [do3cc]


4.0 - 2010-07-18
----------------

- Use the standard libraries doctest module.
  [hannosch]


4.0b1 - 2010-03-01
------------------

- Stopped the cookie from being expired if a redirect (301, 302) or not-modified
  (304) response is sent. This means that if you set a redirect and then
  (superfluously) render a template that would show the status message, you
  won't lose the message.
  [optilude]


4.0a2 - 2009-12-17
------------------

- Changed the default type of a new message from the empty string to info.
  [hannosch]


4.0a1 - 2009-12-17
------------------

- Simplified the interface to use simpler add/show method names while keeping
  backwards compatibility.
  [hannosch]

- More code simplification. Make the code itself independent of Zope2.
  [hannosch]

- Removed a five:implements statement, as the ZPublisher.HTTPRequest is always
  an IBrowserRequest in Zope 2.12.
  [hannosch]

- This version depends on Zope 2.12+.
  [hannosch]

- Package metadata cleanup.
  [hannosch]

- Declare package and test dependencies.
  [hannosch]


3.0.3 - 2007-11-24
------------------

- Use binascii.b2a_base64 instead of base64.encodestring; the former doesn't
  inject newlines every 76 characters, which makes it easier to strip just the
  last one (slightly faster). This fixes tickets #7323 and #7325.
  [mj]


3.0.2 - 2007-11-06
------------------

- Fixed encoding format for the cookie value. The former format imposed a
  serious security risk. The full security issue is tracked at:
  http://cve.mitre.org/cgi-bin/cvename.cgi?name=CVE-2007-5741. This also fixes
  http://dev.plone.org/plone/ticket/6943.
  [hannosch, witsch, mj]


3.0.1 - 2007-10-07
------------------

- Added the IAttributeAnnotatable interface assignment for the request to this
  package as well as the inclusion of the zope.annotation, as we rely on it.
  [hannosch]


3.0 - 2007-08-09
----------------

- No changes.
  [hannosch]


3.0rc1 - 2007-07-10
-------------------

- Removed useless setup.cfg.
  [hannosch]


3.0b2 - 2007-03-23
------------------

- Fixed duplicate message bug. Showing identical messages to the end user more
  than once, doesn't make any sense. This closes
  http://dev.plone.org/plone/ticket/6109.
  [hannosch]

- Added 's support for statusmessages without a redirect. This uses annotations
  on the request instead of direct values, so we avoid the possibility of
  sneaking those in via query strings.
  [tomster, hannosch]


3.0b1 - 2007-03-05
------------------

- Converted to a package in the Products namespace.
  [hannosch]

- Added explicit translation of statusmessages before storing them in the
  cookie. This makes sure we have a reasonable context to base the
  translation on.
  [hannosch]

- Changed license to BSD, to make it possible to include it as a dependency
  in Archetypes.
  [hannosch]


2.1 - 2006-10-25
----------------

- Updated test infrastructure, removed custom testrunner.
  [hannosch]

- Fixed deprecation warning for the zcml content directive.
  [hannosch]


2.0 - 2006-05-15
----------------

- Total reimplementation using cookies instead of a server-side in-memory
  storage to store status messages. The reasoning behind this change is that
  the former approach didn't play well with web caching strategies and added an
  additional burden in ZEO environments (having to use load-balancers, which
  are able to identify users and keep them connected to the same ZEO server).
  [hannosch]


1.1 - 2006-02-13
----------------

- Added tests for ThreadSafeDict.
  [hannosch]

- Fixed serious memory leak and did some code improvements.
  [hannosch, alecm]


1.0 - 2006-01-26
----------------

- Initial implementation
  [hannosch]
