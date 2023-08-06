0.4.12 (released 2018-06-29)
----------------------------

- Paths can now target the parent directory when loading one template relative
  to another (eg ``<py:extends href="../layout.html">``)

0.4.11 (released 2017-09-21)
----------------------------

- Bugfix: <py:include> now works from within a <py:def> function block

0.4.10 (released 2017-09-21)
----------------------------

- Bugfix: fixed parse error when encountering numeric entities in HTML
  templates

0.4.9 (released 2017-09-15)
---------------------------

- Added <py:filter> directive

0.4.8 (released 2017-07-22)
---------------------------

- More robust handling of exceptions arising from template code
- Added <py:tag> directive to allow HTML tag names to be dynamically generated

0.4.7 (released 2017-04-20)
---------------------------

- Bugfix: unicode characters in unescaped interpolations no longer raise
  an exception in python 2.

0.4.6 (released 2017-04-19)
---------------------------

- Added ``{% import path/to/template.txt as foo %}`` text template directive
- Bugfix: fixed parsing error with quoted values in expressions contained
  within template directives.
- Bugfix: calling template functions from unescaped interpolations
  (eg ``$!{myfunc()}`` no longer raises an exception.

0.4.5 (released 2017-03-13)
---------------------------

- Rename project to piglet-templates
- Fix error with nested <py:call> directives

0.4.4 (released 2017-01-08)
---------------------------

- py:extends: allow the 'href' attribute to contain interpolations, eg
  ``<py:extends href="${template}.html>"``
- i18n: added a babel extractor plugin for text templates
- Bugfix: whitespace in translated strings is now correctly normalized
- Bugfix: fixed crash in text templates when using
  ``{% if %}...{% else %}...{% end %}`` blocks

0.4.3 (released 2016-11-29)
---------------------------

- Loader: an ``extension_map`` argument can be given, mapping file extensions
  to template classes. By default ``.txt`` is mapped to
  `piglet.template.TextTemplate` and ``.html`` to
  `piglet.template.HTMLTemplate`.
- Bugfix: unicode symbols no longer cause an exception when used in template
  expressions in Python 2.
- Bugfix: fixed multiple scoping issue with variable names used in
  the argument lists of ``<py:def>`` template function directives.

0.4.2 (released 2016-11-08)
---------------------------

- Added <py:comment> directive
- Exceptions are now reraised, ensuring the originating traceback is shown.
- ``<py:call>`` Now passes its inner HTML as a positional argument, unless it
  is whitespace.
- ``<py:call>`` is now an inner directive, meaning that
  ``<p py:call="foo()"></p>``
  will now fill the ``<p>`` element rather than replacing it.
- The loader cache directory may be specified via the ``PIGLET_CACHE``
  environment variable.
- Added i18n:comment directive

0.4.1 (released 2016-10-17)
---------------------------

- Added ``{% def %}`` and ``{% for %}`` text template directives
- Added ``allow_absolute_paths`` option to TemplateLoader

0.4 (released 2016-10-16)
-------------------------

- Bugfix: ensure ``<py:else>`` directives are always attached to the correct
  ``<py:if>``
- Added ``i18n:trans`` as an alias for i18n:translate
- ``i18n:name`` directives now have a shorter alias
  (``i18n:s``, for substitution) and can take an optional expr attribute,
  eg ``<i18n:s name="foo" expr="calculate_foo()"/>``
- Interpolations in translated strings are now extracted using the
  interpolation text as a placeholder in the absence of a
  ``i18n:name`` directive
- ``py:whitespace="strip"`` no longer strips whitespace between tags
  on the same line.
- Text template directives now include ``{% with %}``,
  ``{% extends %}`` and ``{% block %}``
- <py:extend> can now be used to load a template of the same name elsewhere
  on the template search path.
- The search algorithm used by TemplateLoader is improved
- Bugfix: fix for duplicate rendering when super() is used in the middle of the
  inheritance chain
- Generated code uses ``yield from`` where it supported by the python version.
- The caching code has been simplified, caching .py files to disk containing
  the compiled python source.
- Bugfix: ``py:attrs`` no longer raises an exception
- Bugfix: interpolations can now contain entity references


0.3 (released 2016-10-03)
-------------------------

- The translation code now normalizes whitespace in i18n:messages
- Bugfix: fixed extraction of translations within ``<py:else>`` blocks
- Added translation support in text templates

0.2 (released 2016-10-02)
-------------------------

- Bugfix: ensure that grammar files are included in binary distributions
- Bugfix: fix for undefined variable error when using py:with to reassign
  a variable

0.1 (released 2016-10-01)
-------------------------

- initial release
